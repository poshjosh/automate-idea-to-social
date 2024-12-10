import imghdr
import logging
import os.path
import uuid
from typing import Union

from pyu.io.file import create_file
from .app import App
from .config import RunArg, AppConfig, AgentConfig
from .config_loader import ConfigLoader
from .env import get_upload_file, is_production
from .result.result_set import AgentResultSet

CONFIG_PATH = os.path.join(os.getcwd(), 'resources', 'config')

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class WebService:
    def __init__(self, app_config: dict[str, any] = None):
        config_loader = ConfigLoader(CONFIG_PATH)
        self.agent_configs = {}
        for k, v in config_loader.load_agent_configs().items():
            agent_config = AgentConfig(v)
            if is_production() is False or 'test' not in agent_config.get_agent_tags():
                self.agent_configs[k] = agent_config
        if not app_config:
            app_config = config_loader.load_app_config()
        self.app_config = AppConfig(app_config)

    def index(self) -> dict[str, str]:
        return {'title': self.app_config.get_title(), 'heading': self.app_config.get_title()}

    def automate_task(self, tag) -> dict[str, any]:
        agents = {}
        for e in self._get_agent_names(tag):
            agents[e] = e.replace('-', ' ')
        return {
            'title': self.app_config.get_title(),
            'heading': self._get_heading_for_tag(tag),
            'agents': agents,
            'tag': tag}

    def automate(self) -> dict[str, any]:
        return {'title': self.app_config.get_title(), 'heading': 'Automate tasks using agents.'}

    @staticmethod
    def automate_start(form, files) -> AgentResultSet:
        try:
            form_data = dict(form)
            form_data.update(_save_files(str(uuid.uuid4()), files))
            logger.debug(f"Form data: {form_data}")

            agent_names = form.getlist(RunArg.AGENTS.value)
            try:
                run_config = RunArg.of_dict(form_data)
            except ValueError as value_ex:
                raise ValidationError(value_ex.args[0])
            run_config = {
                **run_config,
                RunArg.CONTINUE_ON_ERROR.value: True,
                RunArg.AGENTS.value: agent_names
            }
            return App.of_defaults(ConfigLoader(CONFIG_PATH, run_config)).run(run_config)
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def _get_agent_names(self, tag) -> list[str]:
        return [name for name, cfg in self.agent_configs.items() if tag in cfg.get_agent_tags()]

    def _get_heading_for_tag(self, tag):
        if tag == 'generate-video':
            return 'Enter details of video to generate'
        elif tag == 'generate-image':
            return 'Enter details of image to generate'
        elif tag == 'post':
            return 'Enter details of content to post'
        elif tag == 'custom':
            return 'Enter details'
        elif tag == 'test':
            return 'Enter details'
        else:
            raise NotImplementedError(f"Unknown tag: {tag}")


def _secure_filename(filename: str) -> str:
    # TODO - Implement this or use a library function like: werkzeug.utils.secure_filename
    return filename


def _get_image_ext(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    file_ext = imghdr.what(None, header)
    if not file_ext:
        return None
    return '.' + file_ext


def _validate_image_ext(uploaded_file):
    file_ext = os.path.splitext(uploaded_file.filename)[1]
    if file_ext not in [".jpeg", ".jpg"]:
        raise ValidationError(f"Invalid file type: {file_ext}")
    img_ext = _get_image_ext(uploaded_file.stream)
    if not img_ext or img_ext not in [".jpeg", ".jpg"]:
        raise ValidationError(f"Invalid image type: {img_ext}")


def _save_file(task_id, files, input_name) -> Union[str, None]:
    uploaded_file = files.get(input_name)
    if not uploaded_file:
        return None
    if not uploaded_file.filename:
        return None
    if input_name == RunArg.VIDEO_COVER_IMAGE.value or \
            input_name == RunArg.VIDEO_COVER_IMAGE_SQUARE.value:
        _validate_image_ext(uploaded_file)
    filepath = get_upload_file(task_id, _secure_filename(uploaded_file.filename))
    logger.debug(f"Will save: {input_name} to {filepath}")
    create_file(filepath)
    uploaded_file.save(filepath)
    return filepath


def _save_files(task_id, files) -> dict[str, any]:
    saved_files = {}
    for e in RunArg:
        run_arg = RunArg(e)
        if not run_arg.is_path:
            continue
        saved_file = _save_file(task_id, files, run_arg.value)
        if not saved_file:
            continue
        saved_files[run_arg.value] = saved_file
    return saved_files

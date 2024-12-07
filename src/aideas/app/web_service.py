import imghdr
import logging
import os.path
import uuid
from typing import Union

from pyu.io.file import create_file
from .app import App
from .config import RunArg, AppConfig
from .config_loader import ConfigLoader
from .env import get_downloads_file_path
from .result.result_set import AgentResultSet

CONFIG_PATH = os.path.join(os.getcwd(), 'resources', 'config')

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class WebService:
    def __init__(self, app_config: dict[str, any] = None):
        self.app_config = app_config if app_config is not None \
            else AppConfig(ConfigLoader(CONFIG_PATH).load_app_config())

    def index(self) -> dict[str, str]:
        return {'title': self.app_config.get_title(), 'heading': self.app_config.get_title()}

    def automate(self) -> dict[str, any]:
        agents = {}
        for e in self.app_config.get_agents():
            agents[e] = e.replace('-', ' ')
        return {
            'title': self.app_config.get_title(),
            'heading': 'Enter details of post to automatically send',
            'agents': agents}

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
                logger.exception(value_ex)
                test_agents = [e for e in agent_names if e.startswith("test-")]
                if len(test_agents) == len(agent_names):
                    logger.info("Ignore previous error as test agents generally work "
                                "even without video content related fields")
                    run_config = form_data
                else:
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


def _secure_filename(filename: str) -> str:
    return filename


def _get_image_ext(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    file_ext = imghdr.what(None, header)
    if not file_ext:
        return None
    return '.' + (file_ext if file_ext != 'jpeg' else 'jpg')


def _validate_image_ext(uploaded_file):
    file_ext = os.path.splitext(uploaded_file.filename)[1]
    if file_ext not in [".jpeg", ".jpg"] or \
            file_ext != _get_image_ext(uploaded_file.stream):
        raise ValidationError(f"Invalid file type: {file_ext}")


def _save_file(session_id, files, input_name) -> Union[str, None]:
    uploaded_file = files.get(input_name)
    if not uploaded_file:
        return None
    filename = _secure_filename(uploaded_file.filename)
    if not filename:
        return None
    if input_name == RunArg.VIDEO_COVER_IMAGE.value or \
            input_name == RunArg.VIDEO_COVER_IMAGE_SQUARE.value:
        _validate_image_ext(uploaded_file)
    filepath = get_downloads_file_path(session_id, filename)
    logger.debug(f"Will save: {input_name} to {filepath}")
    create_file(filepath)
    uploaded_file.save(filepath)
    return filepath


def _save_files(session_id, files) -> dict[str, any]:
    saved_files = {}
    for e in RunArg:
        run_arg = RunArg(e)
        if not run_arg.is_path:
            continue
        saved_file = _save_file(session_id, files, run_arg.value)
        if not saved_file:
            continue
        saved_files[run_arg.value] = saved_file
    return saved_files

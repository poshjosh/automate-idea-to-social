import imghdr
import logging
import os.path
from typing import Union, Callable

from pyu.io.file import create_file
from .config import RunArg, AppConfig, AgentConfig
from .config_loader import ConfigLoader
from .env import get_upload_file, is_production
from .task import Task, add_task, get_task_ids, require_task, submit_task

CONFIG_PATH = os.path.join(os.getcwd(), 'resources', 'config')

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class WebService:
    def __init__(self, config_loader: ConfigLoader):
        self.__config_loader = config_loader
        self.app_config = AppConfig(config_loader.load_app_config())

    def index(self) -> dict[str, str]:
        return {'title': self.app_config.get_title(), 'heading': self.app_config.get_title()}

    def automate_task(self, tag) -> dict[str, any]:
        agents = {}
        for agent_name in self._get_agent_names(tag):
            agents[agent_name] = agent_name.replace('-', ' ')
        return {
            'title': self.app_config.get_title(),
            'heading': self._get_heading_for_tag(tag),
            'agents': agents,
            'tag': tag}

    def automate(self) -> dict[str, any]:
        return {'title': self.app_config.get_title(), 'heading': 'Automate tasks using agents'}

    def automate_start_async(self, task_id: str, form, files) -> Task:
        try:
            task = self.new_task(task_id, form, files)
            submit_task(task_id, task)
            return task
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def automate_start(self, task_id: str, form, files) -> Task:
        try:
            return add_task(task_id, self.new_task(task_id, form, files)).start()
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def new_task(self, task_id: str, form, files) -> Task:
        try:
            form_data = dict(form)
            form_data.update(_save_files(task_id, files))
            logger.debug(f"Form data: {form_data}")

            agent_names = form.getlist(RunArg.AGENTS.value)
            try:
                run_config = RunArg.of_dict(form_data)
            except ValueError as value_ex:
                raise ValidationError(value_ex.args[0])

            run_config = {**run_config, RunArg.AGENTS.value: agent_names}

            return Task.of_defaults(self.__config_loader, run_config)
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def tasks(self,
              get_task_links: Callable[[str], dict[str, any]],
              info: str = None) -> dict[str, any]:
        task_ids: [str] = get_task_ids()
        tasks = []
        for task_id in task_ids:
            tasks.append({
                'id': task_id,
                'agents': require_task(task_id).get_agent_names(),
                'links': get_task_links(task_id)
            })
        return {'title': self.app_config.get_title(), 'heading': 'Tasks',
                'tasks': tasks, 'info': info}

    def _get_agent_names(self, tag: str) -> list[str]:
        def config_filter(config: dict[str, any]) -> bool:
            agent_tags = AgentConfig(config).get_agent_tags()
            if is_production() is True and 'test' in agent_tags:
                return False
            return tag in agent_tags

        def config_sort(config: dict[str, any]) -> int:
            return AgentConfig(config).get_sort_order()

        return self.__config_loader.get_sorted_agent_names(config_filter, config_sort)

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

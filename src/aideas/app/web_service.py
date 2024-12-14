import logging
import os.path
from typing import Callable

from .config import RunArg, AppConfig, AgentConfig
from .config_loader import ConfigLoader
from .env import is_production
from .image_service import save_files
from .task import AgentTask, Task, add_task, get_task_ids, require_task, submit_task

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
        self.default_page_variables = {
            'app_name': self.app_config.get_app_name(),
            'title': self.app_config.get_title(),
            'heading': self.app_config.get_title()
        }

    def index(self) -> dict[str, str]:
        return self._with_default_page_variables()

    def automation_details_form(self, tag) -> dict[str, any]:
        agents = {}
        for agent_name in self._get_agent_names(tag):
            agents[agent_name] = agent_name.replace('-', ' ')
        return self._with_default_page_variables({'agents': agents, 'tag': tag})

    def automation_index(self) -> dict[str, any]:
        return self._with_default_page_variables()

    def start_automation_async(self, task_id: str, form, files) -> Task:
        try:
            task = self.new_task(task_id, form, files)
            submit_task(task_id, task)
            return task
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def start_automation(self, task_id: str, form, files) -> Task:
        try:
            task = self.new_task(task_id, form, files)
            add_task(task_id, task).start()
            return task
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def new_task(self, task_id: str, form, files) -> Task:
        try:
            form_data = dict(form)
            try:
                form_data.update(save_files(task_id, files))
                logger.debug(f"Form data: {form_data}")
                run_config = RunArg.of_dict(form_data)
            except ValueError as value_ex:
                raise ValidationError(value_ex.args[0])

            agent_names = form.getlist(RunArg.AGENTS.value)

            run_config = {**run_config, RunArg.AGENTS.value: agent_names}

            return AgentTask.of_defaults(self.__config_loader, run_config)
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def tasks(self,
              get_task_links: Callable[[str], dict[str, any]],
              info: str = None) -> dict[str, any]:
        task_ids: [str] = get_task_ids()
        tasks = []
        for task_id in task_ids:
            task: AgentTask = require_task(task_id)
            tasks.append({
                'id': task_id,
                'agents': task.get_run_context().get_agent_names(),
                'links': get_task_links(task_id)
            })
        return self._with_default_page_variables({'tasks': tasks, 'info': info})

    def _with_default_page_variables(self, variables: dict[str, any] = None):
        if variables is None:
            variables = {}
        for key, value in self.default_page_variables.items():
            if key not in variables.keys():
                variables[key] = value
        return variables

    def _get_agent_names(self, tag: str) -> list[str]:
        def config_filter(config: dict[str, any]) -> bool:
            agent_tags = AgentConfig(config).get_agent_tags()
            if is_production() is True and 'test' in agent_tags:
                return False
            return tag in agent_tags

        def config_sort(config: dict[str, any]) -> int:
            return AgentConfig(config).get_sort_order()

        return self.__config_loader.get_sorted_agent_names(config_filter, config_sort)

import logging
from typing import Callable

from .config import AppConfig, AgentConfig
from .config_loader import ConfigLoader
from .env import is_production, has_env_value
from .i18n import I18n
from .task import AgentTask, Task, add_task, get_task_ids, require_task, submit_task

logger = logging.getLogger(__name__)


class HtmlFormat:
    @staticmethod
    def display(name: str) -> str:
        return name.replace('-', ' ').replace('_', ' ').title()

    @staticmethod
    def form_field_name(name: str) -> str:
        return name.lower().replace('_', '-').replace(' ', '-')

class WebService:
    def __init__(self, config_loader: ConfigLoader):
        self.__config_loader = config_loader
        self.app_config = AppConfig(config_loader.load_app_config())
        self.default_page_variables = {
            'app_name': self.app_config.get_app_name(),
            'title': self.app_config.get_title(),
            'heading': self.app_config.get_title(),
            'supported_languages': I18n.get_supported_languages()
        }

    def index(self, page_variables: dict[str, any] = None) -> dict[str, str]:
        return self._with_default_page_variables(page_variables)

    def automation_index(self, page_variables: dict[str, any] = None) -> dict[str, any]:
        return self._with_default_page_variables(page_variables)

    def select_automation_agents(self, tag) -> dict[str, any]:
        agents = {}
        for agent_name in self._get_agent_names(tag):
            agents[agent_name] = HtmlFormat.display(agent_name)
        return self._with_default_page_variables({'tag': tag, 'agents': agents})

    def enter_automation_details(self, data: dict[str, any]) -> dict[str, any]:
        tag = data['tag']
        agent_names = data['agents']

        agents = {}
        all_form_fields = []
        for agent_name in agent_names:
            agents[agent_name] = HtmlFormat.display(agent_name)
            variables: [str] = self.__config_loader.get_agent_variable_names(agent_name)
            form_fields = [HtmlFormat.form_field_name(e)
                           for e in variables if has_env_value(e) is False]
            logger.debug(f"Agent {agent_name} form fields: {form_fields}")
            all_form_fields.extend(form_fields)

        # Input order preserved
        # all_form_fields = list(dict.fromkeys(all_form_fields))

        # Natural order sorted
        all_form_fields = list(set(all_form_fields))
        all_form_fields.sort()

        return self._with_default_page_variables(
            {'tag': tag, 'agents': agents, 'form_fields': all_form_fields})

    def start_automation_async(self, task_id: str, data: dict[str, any]) -> Task:
        try:
            task = AgentTask.of_defaults(self.__config_loader, data)
            submit_task(task_id, task)
            return task
        except Exception as ex:
            logger.exception(ex)
            raise ex

    def start_automation(self, task_id: str, data: dict[str, any]) -> Task:
        try:
            task = AgentTask.of_defaults(self.__config_loader, data)
            add_task(task_id, task).start()
            return task
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

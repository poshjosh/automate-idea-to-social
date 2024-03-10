import logging
from typing import Union

from .agent import Agent
from .agent_name import AgentName
from .blog_agent import BlogAgent
from .browser_agent import BrowserAgent
from .translation.translation_agent import TranslationAgent
from ..config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class AgentFactory:
    def __init__(self, config_loader: ConfigLoader, app_config: dict[str, any] = None):
        self.__config_loader = config_loader
        self.__app_config = config_loader.load_app_config() if app_config is None else app_config

    def get_agent(self, agent_name: str) -> Agent:
        agent_config: dict[str, any] = self.__load_agent_config(agent_name)
        return self.__create_agent(agent_name, agent_config)

    def __create_agent(self,
                       agent_name: str,
                       agent_config: dict[str, any]) -> Agent:
        if agent_name == AgentName.TRANSLATION:
            agent = self.create_translation_agent(agent_config)
        elif agent_name == AgentName.BLOG:
            agent = self.create_blog_agent(agent_config)
        else:
            agent = self.create_browser_agent(agent_name, agent_config)

        self.__add_dependencies(agent)
        return agent

    def create_browser_agent(self,
                             agent_name: str,
                             agent_config,
                             dependencies: Union[dict[str, Agent], None] = None) -> BrowserAgent:
        return BrowserAgent.of_config(agent_name, self.__app_config, agent_config, dependencies)

    def create_translation_agent(self, agent_config) -> TranslationAgent:
        return TranslationAgent.of_config(agent_config)

    def create_blog_agent(self, agent_config) -> BlogAgent:
        return BlogAgent.of_config(agent_config)

    def __add_dependencies(self, author: Union[Agent, None]):
        author_name = author.get_name()
        author_config = author.get_config()
        dependencies: [str] = author_config.get('depends-on', [])
        for dep_name in dependencies:
            dep_config = self.__load_agent_config(dep_name)
            if author_name in dep_config.get('depends-on', []):
                # We try to detect some circular dependencies. Other circular
                # dependencies will be detected by the recursive call involved.
                raise ValueError(f'Circular dependency detected: '
                                 f'{author_name} depends on {dep_name} and vice-versa')
            dep = self.__create_dependency(author, dep_name, dep_config, None)

            if dep is None:
                continue

            logger.debug(f'Adding dependency: {dep_name} to agent {author.get_name()}')

            # NOTE: Dependency is stored with own name
            #
            author.add_dependency(dep_name, dep)

    @staticmethod
    def __create_dependency(author: Agent,
                            dep_name: str,
                            dep_config: dict[str, any],
                            result_if_none: Union[Agent, None] = None) -> Agent:
        if isinstance(author, BrowserAgent):
            # We create browser agent dependency using the author's browser agent.
            # We do this so that browser agents and their dependencies
            # share the same browser
            #
            # NOTE: Dependency is created with the author's name
            #
            return author.create_dependency(author.get_name(), dep_config)
        return result_if_none

    def get_app_config(self) -> dict[str, any]:
        return self.__app_config

    def get_config_loader(self) -> ConfigLoader:
        return self.__config_loader

    def __load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.__config_loader.load_agent_config(agent_name)

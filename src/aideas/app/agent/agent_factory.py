import logging
from typing import Union

from .agent import Agent
from .agent_name import AgentName
from .blog_agent import BlogAgent
from .browser_agent import BrowserAgent
from .translation.subtitles_translation_agent import SubtitlesTranslationAgent
from .translation.translation_agent import TranslationAgent
from ..config import AgentConfig, AgentType
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
        agent_type = AgentConfig(agent_config).get_agent_type()
        if agent_name == AgentName.TRANSLATION:
            agent = self.create_translation_agent(agent_name, agent_config)
        elif agent_name == AgentName.SUBTITLES_TRANSLATION:
            agent = self.create_subtitles_translation_agent(agent_name, agent_config)
        elif agent_type == AgentType.BLOG:
            agent = self.create_blog_agent(agent_name, agent_config)
        elif agent_type == AgentType.GENERIC:
            agent = self.create_generic_agent(agent_name, agent_config)
        elif agent_type == AgentType.LLM:
            raise NotImplementedError(f'{agent_type} is not yet implemented')
        elif agent_type == AgentType.BROWSER:
            agent = self.create_browser_agent(agent_name, agent_config)
        else:
            raise ValueError(f'Unknown agent type: {agent_type}')

        self.__add_dependencies(agent)
        return agent

    def create_blog_agent(self,
                          agent_name: str,
                          agent_config,
                          dependencies: Union[dict[str, Agent], None] = None) -> BlogAgent:
        return BlogAgent.of_config(agent_name, self.__app_config, agent_config, dependencies)

    def create_browser_agent(self,
                             agent_name: str,
                             agent_config,
                             dependencies: Union[dict[str, Agent], None] = None) -> BrowserAgent:
        return BrowserAgent.of_config(agent_name, self.__app_config, agent_config, dependencies)

    def create_generic_agent(
            self,
            agent_name: str,
            agent_config,
            dependencies: Union[dict[str, Agent], None] = None) -> Agent:
        return Agent.of_config(agent_name, self.__app_config, agent_config, dependencies)

    def create_translation_agent(
            self,
            agent_name: str,
            agent_config,
            dependencies: Union[dict[str, Agent], None] = None) -> TranslationAgent:
        return TranslationAgent.of_config(agent_name, self.__app_config, agent_config, dependencies)

    def create_subtitles_translation_agent(
            self,
            agent_name: str,
            agent_config,
            dependencies: Union[dict[str, Agent], None] = None) -> SubtitlesTranslationAgent:
        return SubtitlesTranslationAgent.of_config(agent_name, self.__app_config, agent_config, dependencies)

    def __add_dependencies(self, author: Union[Agent, None]):
        author_name = author.get_name()
        author_config: AgentConfig = author.get_config()
        dependencies: [str] = author_config.get_depends_on()
        for dep_name in dependencies:

            # We choose not to check if variables in the dependencies config have been replaced.
            # Even though instagram depends on facebook for login, instagram does not need the
            # facebook variable `video-file-landscape` to be available for it to succeed.
            # Facebook variables common to instagram should already be available.
            dep_config = self.__load_agent_config(dep_name, False)

            if author_name in AgentConfig(dep_config).get_depends_on():
                # We try to detect some circular dependencies. Other circular
                # dependencies will be detected by the recursive call involved.
                raise ValueError(f'Circular dependency detected: '
                                 f'{author_name} depends on {dep_name} and vice-versa')
            dep = self.__create_dependency(author, dep_config)

            if dep is None:
                continue

            logger.debug(f'Adding dependency: {dep_name} to agent {author.get_name()}')

            # NOTE: Dependency is stored with own name
            #
            author.add_dependency(dep_name, dep)

    @staticmethod
    def __create_dependency(author: Agent, dep_config: dict[str, any]) -> Agent:
        # We create the agent's dependency using the author's agent.
        # We do this so that agents and their dependencies share the same resources.
        # For example, browser agents and their dependencies share the same webdriver.
        #
        # NOTE: Dependency is created with the author's name
        #
        return author.create_dependency(author.get_name(), dep_config)

    def get_app_config(self) -> dict[str, any]:
        return self.__app_config

    def get_config_loader(self) -> ConfigLoader:
        return self.__config_loader

    def __load_agent_config(self, agent_name: str, check_variables_replaced = True) -> dict[str, any]:
        return self.__config_loader.load_agent_config(agent_name, check_variables_replaced)

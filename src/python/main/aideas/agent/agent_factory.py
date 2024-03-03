from .agent import Agent
from .agent_name import AgentName
from .browser_agent import BrowserAgent
from .translation.translation_agent import TranslationAgent


class AgentFactory:
    def __init__(self, app_config: dict[str, any] = None):
        self.__app_config = app_config

    def get_agent(self, agent_name: str, agent_config: dict[str, any]) -> Agent:
        if agent_name == AgentName.TRANSLATION:
            return self.create_translation_agent(agent_config)
        else:
            return self.create_browser_agent(agent_name, agent_config)

    def create_browser_agent(self, agent_name: str, agent_config) -> BrowserAgent:
        return BrowserAgent.of_config(agent_name, self.__app_config, agent_config)

    def create_translation_agent(self, agent_config) -> TranslationAgent:
        return TranslationAgent.of_config(agent_config)

    def get_app_config(self) -> dict[str, any]:
        return self.__app_config

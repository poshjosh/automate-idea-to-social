from .agent import Agent
from .agent_names import AgentNames
from .browser_agent import BrowserAgent
from ..config_loader import ConfigLoader
from .translation.translation_agent import TranslationAgent


class AgentFactory:
    def __init__(self, config: dict[str, any]):
        self.__config = config

    def get_agent(self, agent_name) -> Agent:
        agent_config = ConfigLoader.load_from_id(f'agent/{agent_name}')
        if agent_name == AgentNames.PICTORY:
            return BrowserAgent.of_config(self.__config, agent_config)
        elif agent_name == AgentNames.TRANSLATION:
            return TranslationAgent.of_config(self.__config)
        raise ValueError(f'Agent named `{agent_name}` is not supported')

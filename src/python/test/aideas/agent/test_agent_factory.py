from ..agent.test_browser_agent import TestBrowserAgent
from ..agent.translation.test_translation_agent import TestTranslationAgent
from ....main.aideas.agent.translation.translation_agent import TranslationAgent
from ....main.aideas.agent.browser_agent import BrowserAgent
from ....main.aideas.agent.agent_factory import AgentFactory


class TestAgentFactory(AgentFactory):
    def create_browser_agent(self, agent_name: str, agent_config) -> BrowserAgent:
        return TestBrowserAgent.of_config(agent_name, self.get_app_config(), agent_config)

    def create_translation_agent(self, agent_config) -> TranslationAgent:
        return TestTranslationAgent.of_config(agent_config)

from typing import Union

from test.app.agent.test_blog_agent import TestBlogAgent
from test.app.agent.test_browser_agent import TestBrowserAgent
from test.app.agent.translation.test_translation_agent import TestTranslationAgent
from aideas import Agent
from aideas.app.agent.translation.translation_agent import TranslationAgent
from aideas import BlogAgent
from aideas import BrowserAgent
from aideas.app.agent.agent_factory import AgentFactory


class TestAgentFactory(AgentFactory):
    def create_blog_agent(self,
                          agent_name: str,
                          agent_config,
                          dependencies: Union[dict[str, Agent], None] = None) -> BlogAgent:
        return TestBlogAgent.of_config(agent_name, self.get_app_config(), agent_config, dependencies)

    def create_browser_agent(self,
                             agent_name: str,
                             agent_config,
                             dependencies: Union[dict[str, Agent], None] = None) -> BrowserAgent:
        return TestBrowserAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

    def create_translation_agent(
            self,
            agent_name: str,
            agent_config,
            dependencies: Union[dict[str, Agent], None] = None) -> TranslationAgent:
        return TestTranslationAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

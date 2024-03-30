from typing import Union

from ..agent.test_blog_agent import TestBlogAgent
from ..agent.test_browser_agent import TestBrowserAgent
from ..agent.translation.test_translation_agent import TestTranslationAgent
from .....main.app.aideas.agent.agent import Agent
from .....main.app.aideas.agent.translation.translation_agent import TranslationAgent
from .....main.app.aideas.agent.blog_agent import BlogAgent
from .....main.app.aideas.agent.browser_agent import BrowserAgent
from .....main.app.aideas.agent.agent_factory import AgentFactory


class TestAgentFactory(AgentFactory):
    def create_browser_agent(self,
                             agent_name: str,
                             agent_config,
                             dependencies: Union[dict[str, Agent], None] = None) -> BrowserAgent:
        return TestBrowserAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

    def create_translation_agent(self, agent_config) -> TranslationAgent:
        return TestTranslationAgent.of_config(agent_config)

    def create_blog_agent(self, agent_config) -> BlogAgent:
        return TestBlogAgent.of_config(agent_config)

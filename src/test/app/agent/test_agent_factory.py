from typing import Union

from test.app.agent.test_blog_agent import TestBlogAgent
from test.app.agent.test_browser_agent import TestBrowserAgent
from test.app.agent.translation.test_subtitles_translation_agent import TestSubtitlesTranslationAgent
from aideas.app.agent.agent import Agent
from aideas.app.agent.translation.subtitles_translation_agent import SubtitlesTranslationAgent
from aideas.app.agent.blog_agent import BlogAgent
from aideas.app.agent.browser_agent import BrowserAgent
from aideas.app.agent.agent_factory import AgentFactory


class TestAgentFactory(AgentFactory):
    def create_blog_agent(self,
                          agent_name: str,
                          agent_config,
                          dependencies: Union[dict[str, Agent], None] = None) -> BlogAgent:
        return TestBlogAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

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
            dependencies: Union[dict[str, Agent], None] = None) -> SubtitlesTranslationAgent:
        return TestSubtitlesTranslationAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

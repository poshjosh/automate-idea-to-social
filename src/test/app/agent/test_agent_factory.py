from typing import Union

from test.app.agent.test_blog_agent import TestBlogAgent
from test.app.agent.test_browser_automator_agent import TestBrowserAutomatorAgent
from aideas.app.agent.automator_agent import AutomatorAgent
from aideas.app.agent.blog_automator_agent import BlogAutomatorAgent
from aideas.app.agent.browser_automator_agent import BrowserAutomatorAgent
from aideas.app.agent.agent_factory import AgentFactory


class TestAgentFactory(AgentFactory):
    def with_added_variable_source(self, variable_source: dict[str, any]) -> 'AgentFactory':
        return TestAgentFactory(
            self.get_config_loader().with_added_variable_source(variable_source),
            self.get_app_config())

    def create_blog_agent(self,
                          agent_name: str,
                          agent_config,
                          dependencies: Union[dict[str, AutomatorAgent], None] = None) -> BlogAutomatorAgent:
        return TestBlogAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

    def create_browser_agent(self,
                             agent_name: str,
                             agent_config,
                             dependencies: Union[dict[str, AutomatorAgent], None] = None) -> BrowserAutomatorAgent:
        return TestBrowserAutomatorAgent.of_config(
            agent_name, self.get_app_config(), agent_config, dependencies)

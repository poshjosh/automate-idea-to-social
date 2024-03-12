from typing import Union

from ..test_functions import delete_saved_files
from ..web.test_browser_automator import TestBrowserAutomator
from ....main.aideas.agent.agent import Agent
from ....main.aideas.agent.browser_agent import BrowserAgent
from ....main.aideas.event.event_handler import EventHandler
from ....main.aideas.config import Name
from ....main.aideas.result.result_set import ElementResultSet
from ....main.aideas.run_context import RunContext


class TestBrowserAgent(BrowserAgent):
    @staticmethod
    def of_config(agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: Union[dict[str, Agent], None] = None) -> 'BrowserAgent':
        browser_automator = TestBrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get('interval-seconds', 0)
        return TestBrowserAgent(
            agent_name, agent_config, dependencies, browser_automator, interval_seconds)

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        result_set: ElementResultSet = ElementResultSet.none()
        try:
            result_set = super().run_stage(run_context, stage_name)
        finally:
            delete_saved_files(result_set)
        return result_set

    def without_events(self) -> 'BrowserAgent':
        browser_automator = self.get_browser_automator().with_event_handler(EventHandler.noop())
        return TestBrowserAgent(
            self.get_name(), self.get_config().root(), self._get_dependencies(),
            browser_automator, self.get_interval_seconds())

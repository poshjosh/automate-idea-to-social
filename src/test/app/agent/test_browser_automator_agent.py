from typing import Union

from test.app.test_functions import delete_saved_files
from test.app.web.test_browser_automator import TestBrowserAutomator
from aideas.app.agent.agent import INTERVAL_KEY
from aideas.app.agent.automator_agent import AutomatorAgent
from aideas.app.agent.browser_automator_agent import BrowserAutomatorAgent
from aideas.app.config import Name
from aideas.app.result.result_set import ElementResultSet
from aideas.app.run_context import RunContext


class TestBrowserAutomatorAgent(BrowserAutomatorAgent):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: Union[dict[str, AutomatorAgent], None] = None) -> 'BrowserAutomatorAgent':
        browser_automator = TestBrowserAutomator.of(app_config, agent_name, agent_config)
        interval_seconds: int = agent_config.get(INTERVAL_KEY, 0)
        return cls(agent_name, agent_config, dependencies, browser_automator, interval_seconds)

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        result_set: ElementResultSet = ElementResultSet.none()
        try:
            result_set = super().run_stage(run_context, stage_name)
        finally:
            delete_saved_files(result_set)
        return result_set

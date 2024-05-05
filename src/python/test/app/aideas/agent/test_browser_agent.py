from typing import Union

from ..test_functions import delete_saved_files
from ..web.test_browser_automator import TestBrowserAutomator
from .....main.app.aideas.agent.agent import Agent, INTERVAL_KEY
from .....main.app.aideas.agent.browser_agent import BrowserAgent
from .....main.app.aideas.config import Name
from .....main.app.aideas.result.result_set import ElementResultSet
from .....main.app.aideas.run_context import RunContext


class TestBrowserAgent(BrowserAgent):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: Union[dict[str, Agent], None] = None) -> 'BrowserAgent':
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

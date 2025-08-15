from unittest import mock

import unittest

from aideas.app.config import AgentConfig, Name
from aideas.app.run_context import RunContext
from aideas.app.web.browser_automator import BrowserAutomationListener
from test.app.test_functions import get_run_context
from test.app.web.test_browser_automator import TestBrowserAutomator

from pyu.io.file import load_yaml_str


class BrowserAutomatorTest(unittest.TestCase):
    @staticmethod
    def test_on_stage_start_event_called():
        agent_name = "test-agent"
        run_context: RunContext = get_run_context([agent_name])
        app_config = run_context.get_app_config()
        agent_config_yaml = """
stages:
  stage-1:
    events:
      onstart: ask_for_help "Testing ask_for_help" 1
        """
        agent_config = load_yaml_str(agent_config_yaml)
        browser_automator = TestBrowserAutomator.of(app_config.to_dict(), agent_name, agent_config)

        with mock.patch.object(BrowserAutomationListener, "on_start") as on_start:
            browser_automator = browser_automator.with_listener(
                BrowserAutomationListener(agent_name, browser_automator.get_action_handler()))
            browser_automator.act_on_elements(AgentConfig(agent_config), Name.of("stage-1"), run_context)
            on_start.assert_called_once()


if __name__ == '__main__':
    unittest.main()


import logging.config
import unittest

from aideas.app.action.action_handler import ActionError
from aideas.app.agent.automator_agent import AutomatorAgent
from test.app.test_functions import init_logging, get_run_context, run_agent
from aideas.app.agent.browser_automator_agent import BrowserAutomatorAgent
from aideas.app.run_context import RunContext

from pyu.io.file import load_yaml_str

init_logging(logging.config)


class AgentAskForHelpIT(unittest.TestCase):
    def test_ask_for_help_at_stage_item(self):
        agent_name: str = "test-agent"
        run_context: RunContext = get_run_context([agent_name])
        yaml = """
stages:
  stage-1:
    stage-items:
      stage-1-item-1:
        events:
          onstart: ask_for_help "Testing action ask_for_help at stage-1-item-1" 1
        actions:
          - log INFO This is a test log message
        """
        agent_config = load_yaml_str(yaml)
        agent = AutomatorAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)
        try:
            run_agent(agent, run_context)
            self.fail("Should raise ActionError because help was not provided in this test case, but did not.")
        except ActionError:
            logging.info("ActionError raised as expected, test passed.")

    def test_ask_for_help_browser_agent(self):
        agent_name: str = "test-agent"
        run_context: RunContext = get_run_context([agent_name])
        yaml = """
stages:
  stage-1:
    events:
      onstart: ask_for_help "Testing action ask_for_help" 1
    stage-items:
      stage-1-item-1:
        actions:
          - log INFO This is a test log message
        """
        agent_config = load_yaml_str(yaml)
        print("Agent name: %s", agent_name)
        agent = BrowserAutomatorAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)
        try:
            run_agent(agent, run_context)
            self.fail("Should raise ActionError because help was not provided in this test case, but did not.")
        except ActionError:
            logging.info("ActionError raised as expected, test passed.")


if __name__ == '__main__':
    unittest.main()

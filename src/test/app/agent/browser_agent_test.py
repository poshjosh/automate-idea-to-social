import logging.config
import unittest

from test.app.agent.test_browser_agent import TestBrowserAgent
from test.app.test_functions import init_logging, load_agent_config, get_run_context, run_agent
from aideas.app.agent.agent_name import AgentName
from aideas.app.action.element_action_handler import ElementActionHandler
from aideas.app.result.result_set import StageResultSet
from aideas.app.run_context import RunContext

from pyu.io.file import load_yaml_str

init_logging(logging.config)


class BrowserAgentTest(unittest.TestCase):

    def test_run_subprocess(self):
        agent_name: str = "test-agent"
        run_context: RunContext = get_run_context([agent_name])
        yaml = """
stages:
  run_subprocess-stage-1:
    stage-items:
      run_subprocess-stage-1-item-1:
        actions:
          - run_subprocess ls -al
        """
        agent_config = load_yaml_str(yaml)
        agent = TestBrowserAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)

        result: StageResultSet = run_agent(agent, run_context)
        self.assertTrue(result.is_successful())

        self.assertEqual(1, result.size())

    def test_given_successful_result_when_may_proceed_is_false_result_is_successful(self):
        agent_name: str = "test-agent"
        run_context: RunContext = get_run_context([agent_name])
        yaml = """
stages:
  test-conditional-does-not-pollute-results:
    url: https://www.google.com/
    stage-items:
      wait-stage:
        actions: wait 1
      conditional-stage:
        when:
          search-for: //test-xpath
          actions: not is_displayed
        actions: log DEBUG This should not be logged; as the condition above should not pass
        """
        agent_config = load_yaml_str(yaml)
        agent = TestBrowserAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)

        # We use a ElementActionHandler, rather than TestElementActionHandler
        automator = agent.get_automator()
        automator = automator.with_action_handler(
            ElementActionHandler(automator.get_element_selector(), 10))

        agent = agent.with_automator(automator)

        result: StageResultSet = run_agent(agent, run_context)
        self.assertTrue(result.is_successful())

        self.assertEqual(1, result.size())

    def test_agent(self):
        agent_name = "test-agent"
        self._named_agent_should_run_successfully(agent_name, get_run_context([agent_name]))

    def test_pictory(self):
        run_context: RunContext = get_run_context([AgentName.PICTORY])
        self._named_agent_should_run_successfully(AgentName.PICTORY, run_context)

    def _named_agent_should_run_successfully(self, agent_name: str, run_context: RunContext):

        agent_config = load_agent_config(agent_name, False)

        agent = TestBrowserAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)

        result = run_agent(agent, run_context)

        self.assertTrue(result.is_successful())


if __name__ == '__main__':
    unittest.main()

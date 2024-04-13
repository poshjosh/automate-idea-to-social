import logging.config
import unittest

from .test_browser_agent import TestBrowserAgent
from ..test_functions import init_logging, get_config_loader
from .....main.app.aideas.action.action_handler import ActionId
from .....main.app.aideas.agent.agent_name import AgentName
from .....main.app.aideas.action.action import Action
from .....main.app.aideas.action.action_result import ActionResult
from .....main.app.aideas.action.element_action_handler import ElementActionHandler
from .....main.app.aideas.io.file import load_yaml_str
from .....main.app.aideas.result.result_set import StageResultSet
from .....main.app.aideas.run_context import RunContext

init_logging(logging.config)


class BrowserAgentTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_config = get_config_loader().load_app_config()

    def test_given_successful_result_when_may_proceed_is_false_result_is_successful(self):
        agent_name: str = "test-agent"
        run_context: RunContext = RunContext.of_config(self.app_config, agent_name)
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
        agent = TestBrowserAgent.of_config(agent_name, self.app_config, agent_config)

        # We use a ElementActionHandler, rather than TestElementActionHandler
        automator = agent.get_browser_automator()
        automator = automator.with_action_handler(
            ElementActionHandler(automator.get_web_driver(), 10))

        agent = agent.with_automator(automator)

        result: StageResultSet = self._agent_should_run_successfully(agent, run_context)

        self.assertEqual(1, result.size())

    def test_agent(self):
        agent_name = "test-agent"
        run_context: RunContext = RunContext.of_config(self.app_config, agent_name)
        self._named_agent_should_run_successfully(agent_name, run_context)

    # def test_pictory(self):
    #     run_context: RunContext = RunContext.of_config(self.app_config, AgentName.PICTORY)
    #     self._named_agent_should_run_successfully(AgentName.PICTORY, run_context)
    #
    # def test_tiktok(self):
    #     run_context: RunContext = self._given_run_context_with_downloaded_file(AgentName.PICTORY)
    #     self._named_agent_should_run_successfully(AgentName.TIKTOK, run_context)

    def _named_agent_should_run_successfully(self, agent_name: str, run_context: RunContext):

        agent_config = get_config_loader().load_agent_config(agent_name)

        agent = TestBrowserAgent.of_config(agent_name, self.app_config, agent_config)

        self._agent_should_run_successfully(agent, run_context)

    def _agent_should_run_successfully(self, agent, run_context: RunContext) -> StageResultSet:

        result = agent.run(run_context)
        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())

        return result

    def _given_run_context_with_downloaded_file(self, agent_name: str) -> RunContext:
        run_context: RunContext = RunContext.of_config(self.app_config, agent_name)
        stage = AgentName.PictoryStage
        stage_id = stage.SAVE_DOWNLOADED_VIDEO
        target_id = stage.Action.GET_FILE
        action = Action(agent_name, stage_id, target_id,
                        ActionId.GET_NEWEST_FILE_IN_DIR.value,
                        ['/videos/dir', 'mp4', '120'])
        action_result = ActionResult(action, True, 'test-downloaded-video.mp4')
        run_context.add_action_result(
            AgentName.PICTORY, stage.DOWNLOAD_VIDEO_LAYOUT_2, action_result)
        return run_context


if __name__ == '__main__':
    unittest.main()

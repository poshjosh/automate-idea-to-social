import logging.config
import unittest

from test.app.agent.test_browser_agent import TestBrowserAgent
from test.app.test_functions import init_logging, get_run_context, load_agent_config, run_agent
from aideas.app.action.action_handler import ActionId
from aideas.app.agent.agent_name import AgentName
from aideas.app.action.action import Action
from aideas.app.action.action_result import ActionResult
from aideas.app.run_context import RunContext

from pyu.io.file import load_yaml_str

init_logging(logging.config)


class BrowserAgentIT(unittest.TestCase):
    def test_tiktok(self):
        run_context: RunContext = self._given_run_context_with_downloaded_file(AgentName.PICTORY)
        self._named_agent_should_run_successfully(AgentName.TIKTOK, run_context)

    @staticmethod
    def _given_run_context_with_downloaded_file(agent_name: str) -> RunContext:
        run_context: RunContext = get_run_context([agent_name])
        stage = AgentName.PictoryStage
        stage_id = stage.VIDEO_PORTRAIT
        target_id = stage.Action.GET_FILE
        action = Action(agent_name, stage_id, target_id,
                        ActionId.GET_NEWEST_FILE_IN_DIR.value, ['/videos/dir', 'mp4', '120'])
        action_result = ActionResult(action, True, 'test-downloaded-video.mp4')
        run_context.add_action_result(action_result)
        return run_context

    def _named_agent_should_run_successfully(self, agent_name: str, run_context: RunContext):

        agent_config = load_agent_config(agent_name, False)

        agent = TestBrowserAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)

        result = run_agent(agent, run_context)

        self.assertTrue(result.is_successful())


if __name__ == '__main__':
    unittest.main()

import logging.config
import unittest

from .test_browser_agent import TestBrowserAgent
from ..test_functions import init_logging, get_config_loader
from ....main.aideas.action.action_handler import ActionId
from ....main.aideas.agent.agent_name import AgentName
from ....main.aideas.action.action import Action
from ....main.aideas.action.action_result import ActionResult
from ....main.aideas.run_context import RunContext

init_logging(logging.config)


class BrowserAgentTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_config = get_config_loader().load_app_config()

    def test_pictory(self):
        run_context: RunContext = RunContext.of_config(self.app_config, AgentName.PICTORY)
        self.__run_agent(AgentName.PICTORY, run_context)

    def test_tiktok(self):
        run_context: RunContext = self.__given_run_context_with_downloaded_file(AgentName.PICTORY)
        self.__run_agent(AgentName.TIKTOK, run_context)

    def __run_agent(self, agent_name: str, run_context: RunContext):
        agent_config = get_config_loader().load_agent_config(agent_name)
        agent = TestBrowserAgent.of_config(agent_name, self.app_config, agent_config)

        result = agent.run(run_context)
        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())

    def __given_run_context_with_downloaded_file(self, agent_name: str) -> RunContext:
        run_context: RunContext = RunContext.of_config(self.app_config, agent_name)
        stage = AgentName.PictoryStage
        stage_id = stage.SAVE_DOWNLOADED_VIDEO
        target_id = stage.Action.GET_FILE
        action = Action(agent_name, stage_id, target_id,
                        ActionId.GET_NEWEST_FILE.value,
                        ['/videos/dir', 'mp4', '120'])
        action_result = ActionResult(action, True, 'test-downloaded-video.mp4')
        run_context.add_action_result(
            AgentName.PICTORY, stage.DOWNLOAD_VIDEO_LAYOUT_2, action_result)
        return run_context


if __name__ == '__main__':
    unittest.main()

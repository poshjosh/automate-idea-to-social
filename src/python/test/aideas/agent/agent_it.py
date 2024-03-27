import copy
import logging.config
import os
import unittest
from typing import Callable

from ..test_functions import delete_saved_files, get_config_loader, get_test_path, init_logging
from ....main.aideas.agent.agent_name import AgentName
from ....main.aideas.agent.browser_agent import BrowserAgent
from ....main.aideas.config import Name, STAGES_KEY, STAGE_ITEMS_KEY
from ....main.aideas.env import Env
from ....main.aideas.result.result_set import ElementResultSet
from ....main.aideas.run_context import RunContext

init_logging(logging.config)

pictory_agent = AgentName.PICTORY
pictory_stage = AgentName.PictoryStage.SAVE_DOWNLOADED_VIDEO

tiktok_stage = 'tiktok-test-stage'
tiktok_target = 'tiktok-target-id'


class AgentIT(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_config = get_config_loader().load_app_config()

    @staticmethod
    def format_tiktok_config(config: dict) -> dict:
        config = copy.deepcopy(config)
        action_signature = ('get_first_file ${AGENTS_DIR}/' + pictory_agent + '/' +
                            pictory_stage + '/save-file $VIDEO_OUTPUT_TYPE')
        actions: [str] = [action_signature, 'log DEBUG $results.me[0]']
        config[STAGES_KEY][tiktok_stage] = {STAGE_ITEMS_KEY: {tiktok_target: {'actions': actions}}}
        return config

    def test_pictory_saved_video_is_available_for_other_agents(self):
        os.environ[Env.OUTPUT_DIR.value] = (
            get_test_path(os.environ[Env.OUTPUT_DIR.value]))
        os.environ[Env.AGENTS_DIR.value] = get_test_path(os.environ[Env.AGENTS_DIR.value])
        run_context: RunContext = RunContext.of_config(self.app_config, pictory_agent)
        result: ElementResultSet = self.__run_agent(pictory_agent, pictory_stage, run_context)

        def is_stage_result(file_name: str) -> bool:
            return pictory_stage in file_name

        error = False

        try:
            for k in result.keys():
                action_result_list = result.get(k)
                for action_result in action_result_list:
                    file = action_result.get_result()

                    if is_stage_result(file) and not os.path.exists(file):
                        error = True
                        print(f'File not found: {file}')
                        continue

            if error:
                self.fail(f'Failed {pictory_agent}.{pictory_stage}')

            self.__run_agent(
                AgentName.TIKTOK, tiktok_stage, run_context, self.format_tiktok_config)
        finally:
            delete_saved_files(result, is_stage_result)

    def __run_agent(self,
                    agent_name: str,
                    stage_name: str,
                    run_context: RunContext,
                    format_config: Callable[[dict], dict] = None) -> ElementResultSet:
        agent_config = get_config_loader().load_agent_config(agent_name)
        if format_config is not None:
            agent_config = format_config(agent_config)

        # Not TestBrowserAgent
        agent = BrowserAgent.of_config(agent_name, self.app_config, agent_config, {})

        result = agent.run_stage(run_context, Name.of(stage_name))
        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())
        return result


if __name__ == '__main__':
    unittest.main()

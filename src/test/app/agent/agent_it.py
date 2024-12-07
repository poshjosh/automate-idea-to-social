import copy
import logging.config
import os
import unittest
from typing import Callable

from test.app.test_functions import delete_saved_files, init_logging, load_agent_config, \
    get_run_context
from aideas.app.agent.agent_name import AgentName
from aideas.app.agent.browser_agent import BrowserAgent
from aideas.app.config import Name, STAGES_KEY, STAGE_ITEMS_KEY
from aideas.app.result.result_set import ElementResultSet
from aideas.app.run_context import RunContext

init_logging(logging.config)

pictory_agent = AgentName.PICTORY
pictory_stage = AgentName.PictoryStage.VIDEO_LANDSCAPE

tiktok_stage = 'tiktok-test-stage'
tiktok_target = 'tiktok-target-id'


class AgentIT(unittest.TestCase):
    @staticmethod
    def format_tiktok_config(config: dict) -> dict:
        config = copy.deepcopy(config)
        action_signature = ('get_first_file ${OUTPUT_DIR}/agent/' + pictory_agent + '/' +
                            pictory_stage + '/save-file $VIDEO_OUTPUT_TYPE')
        actions: [str] = [action_signature, 'log DEBUG $results.me[0]']
        config[STAGES_KEY][tiktok_stage] = {STAGE_ITEMS_KEY: {tiktok_target: {'actions': actions}}}
        return config

    def test_pictory_saved_video_is_available_for_other_agents(self):
        run_context: RunContext = get_run_context([pictory_agent])
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
        agent_config = load_agent_config(agent_name)
        if format_config is not None:
            agent_config = format_config(agent_config)

        # Not TestBrowserAgent
        agent = BrowserAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config, {})

        result = agent.run_stage(run_context, Name.of(stage_name))
        print(f'Completed. Result:\n{result.pretty_str()}')

        self.assertTrue(result.is_successful())
        return result


if __name__ == '__main__':
    unittest.main()

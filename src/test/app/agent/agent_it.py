import time

import copy
import logging.config
import os
import unittest
from typing import Callable

from aideas.app.action.action_handler import ActionError
from aideas.app.agent.agent import Agent
from test.app.test_functions import delete_saved_files, init_logging, load_agent_config, \
    get_run_context
from aideas.app.agent.agent_name import AgentName
from aideas.app.agent.browser_agent import BrowserAgent
from aideas.app.config import Name, STAGES_KEY, STAGE_ITEMS_KEY
from aideas.app.result.result_set import ElementResultSet, StageResultSet
from aideas.app.run_context import RunContext

from pyu.io.file import load_yaml_str

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
                            pictory_stage + '/save-file $VIDEO_FILE_EXTENSION')
        actions: [str] = [action_signature, 'log DEBUG $results.me[0]']
        config[STAGES_KEY][tiktok_stage] = {STAGE_ITEMS_KEY: {tiktok_target: {'actions': actions}}}
        return config

# TODO This test works when run alone, but fails when run with the next test. Find out why and fix.
#
#     def test_ask_for_help_at_stage(self):
#         agent_name: str = "test-agent"
#         run_context: RunContext = get_run_context([agent_name])
#         yaml = """
# stages:
#   stage-1:
#     events:
#       onstart: ask_for_help "Testing action ask_for_help at stage-1" 1
#         """
#         agent_config = load_yaml_str(yaml)
#         agent = Agent.of_config(
#             agent_name, run_context.get_app_config().to_dict(), agent_config)
#
#         result_set = StageResultSet.none()
#         try:
#             result_set = agent.run(run_context)
#             self.fail("Should raise ActionError because help was not provided in this test case, but did not.")
#         except ActionError:
#             logging.info("ActionError raised as expected, test passed.")
#         finally:
#             [delete_saved_files(result_set.get(k)) for k in result_set.keys()]

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
        agent = Agent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)

        result_set = StageResultSet.none()
        try:
            result_set = agent.run(run_context)
            self.fail("Should raise ActionError because help was not provided in this test case, but did not.")
        except ActionError:
            logging.info("ActionError raised as expected, test passed.")
        finally:
            [delete_saved_files(result_set.get(k)) for k in result_set.keys()]

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
        agent = BrowserAgent.of_config(
            agent_name, run_context.get_app_config().to_dict(), agent_config)

        result_set = StageResultSet.none()
        try:
            result_set = agent.run(run_context)
            self.fail("Should raise ActionError because help was not provided in this test case, but did not.")
        except ActionError:
            logging.info("ActionError raised as expected, test passed.")
        finally:
            [delete_saved_files(result_set.get(k)) for k in result_set.keys()]

    def test_pictory_saved_video_is_available_for_other_agents(self):
        run_context: RunContext = get_run_context([pictory_agent])
        result: ElementResultSet = self.__agent_stage_should_run_successfully(pictory_agent, pictory_stage, run_context)

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

            self.__agent_stage_should_run_successfully(
                AgentName.TIKTOK, tiktok_stage, run_context, self.format_tiktok_config)
        finally:
            delete_saved_files(result, is_stage_result)

    def __agent_stage_should_run_successfully(self,
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

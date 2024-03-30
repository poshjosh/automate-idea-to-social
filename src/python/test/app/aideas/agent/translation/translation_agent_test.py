import logging.config
import unittest

from ...agent.translation.test_translation_agent import TestTranslationAgent
from ...test_functions import delete_saved_files, get_config_loader, init_logging
from ......main.app.aideas.result.result_set import StageResultSet
from ......main.app.aideas.agent.agent_name import AgentName
from ......main.app.aideas.run_context import RunContext

init_logging(logging.config)


class TranslationAgentTest(unittest.TestCase):
    def test_run(self):
        agent_name: str = AgentName.TRANSLATION
        app_config = get_config_loader().load_app_config()
        agent_config = get_config_loader().load_agent_config(agent_name)

        agent = TestTranslationAgent.of_config(agent_config)
        run_context: RunContext = RunContext.of_config(app_config, agent_name)

        result_set: StageResultSet = StageResultSet.none()
        try:
            result: agent.run(run_context)
            print(f'Completed. Result:\n{result_set.pretty_str()}')
        finally:
            [delete_saved_files(result_set.get(k)) for k in result_set.keys()]


if __name__ == '__main__':
    unittest.main()

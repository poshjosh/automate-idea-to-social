import logging.config
import unittest

from test.app.agent.translation.test_translation_agent import TestTranslationAgent
from test.app.test_functions import delete_saved_files, get_config_loader, init_logging
from aideas.app.result.result_set import StageResultSet
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext

init_logging(logging.config)


class TranslationAgentTest(unittest.TestCase):
    def test_run(self):
        agent_name: str = AgentName.TRANSLATION
        app_config = get_config_loader().load_app_config()
        agent_config = get_config_loader().load_agent_config(agent_name)

        agent = TestTranslationAgent.of_config(agent_name, app_config, agent_config)
        run_context: RunContext = RunContext.of_config(app_config, agent_name)

        result_set: StageResultSet = StageResultSet.none()
        try:
            result: agent.run(run_context)
            print(f'Completed. Result:\n{result_set.pretty_str()}')
        finally:
            [delete_saved_files(result_set.get(k)) for k in result_set.keys()]


if __name__ == '__main__':
    unittest.main()

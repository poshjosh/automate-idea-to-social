import logging.config
import unittest
from unittest import mock

from aideas.app.agent.translation.subtitles_translation_agent import SubtitlesTranslationAgent
from aideas.app.agent.translation.translator import Translator
from test.app.test_functions import delete_saved_files, init_logging, get_run_context, \
    load_agent_config
from aideas.app.result.result_set import StageResultSet
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext

init_logging(logging.config)


class SubtitlesTranslationAgentTest(unittest.TestCase):
    @staticmethod
    def test_run():
        agent_name: str = AgentName.SUBTITLES_TRANSLATION
        run_context: RunContext = get_run_context([agent_name])
        agent_config = load_agent_config(agent_name, False)

        with mock.patch.object(Translator, "translate") as translate:
            translate.return_value = ["Fake translation result"]

            agent = SubtitlesTranslationAgent.of_config(
                agent_name, run_context.get_app_config().to_dict(), agent_config)

            result_set: StageResultSet = StageResultSet.none()
            try:
                result: agent.run(run_context)
                print(f'Completed. Result:\n{result_set.pretty_str()}')
            finally:
                [delete_saved_files(result_set.get(k)) for k in result_set.keys()]


if __name__ == '__main__':
    unittest.main()

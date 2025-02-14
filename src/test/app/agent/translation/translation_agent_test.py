import logging.config
import os
import unittest
from unittest import mock

from aideas.app.agent.translation.translation_agent import TranslationAgent
from aideas.app.agent.translation.translator import Translator
from test.app.test_functions import delete_saved_files, init_logging, get_run_context, \
    load_agent_config
from aideas.app.result.result_set import StageResultSet
from aideas.app.agent.agent_name import AgentName
from aideas.app.run_context import RunContext

init_logging(logging.config)

agent_name: str = AgentName.TRANSLATION

class TranslationAgentTest(unittest.TestCase):
    agent_name: str = AgentName.TRANSLATION
    @staticmethod
    def test_run():
        run_context: RunContext = get_run_context([agent_name])
        agent_config = load_agent_config(agent_name)

        with mock.patch.object(Translator, "translate") as translate:
            translate.return_value = ["Fake translation result"]

            agent: TranslationAgent = TranslationAgent.of_config(
                agent_name, run_context.get_app_config().to_dict(), agent_config)

            result_set: StageResultSet = StageResultSet.none()
            try:
                result: agent.run(run_context)
                print(f'Completed. Result:\n{result_set.pretty_str()}')
            finally:
                [delete_saved_files(result_set.get(k)) for k in result_set.keys()]

    def test_get_output_file_path(self):
        parent_dir = "parent-dir"
        result = self._test_get_output_file_path("en", "Hello world", "de", "Hallo Welt", parent_dir)
        expected_result = os.path.join(parent_dir, "Hallo Welt.txt")
        self.assertEqual(result, expected_result)

    def test_get_output_file_path_when_filename_not_translated(self):
        parent_dir = "parent-dir"
        text = "Hello world"
        result = self._test_get_output_file_path("en", text, "de", text, parent_dir)
        expected_result = os.path.join(parent_dir, f"{text}.de.txt")
        self.assertEqual(result, expected_result)

    @staticmethod
    def _test_get_output_file_path(
            src_lang_code: str, text: str,
            tgt_lang_code: str, text_translated: str, parent_dir: str = "parent-dir") -> str:
        run_context: RunContext = get_run_context([agent_name])
        agent_config = load_agent_config(agent_name)

        with mock.patch.object(Translator, "translate") as translate:
            translate.return_value = [text_translated]

            agent: TranslationAgent = TranslationAgent.of_config(
                agent_name, run_context.get_app_config().to_dict(), agent_config)

            input_file_path = os.path.join(parent_dir, f"{text}.txt")
            result = agent._get_output_file_path(input_file_path, tgt_lang_code)

            translate.assert_called_once_with(text, src_lang_code, tgt_lang_code)

            return result


if __name__ == '__main__':
    unittest.main()

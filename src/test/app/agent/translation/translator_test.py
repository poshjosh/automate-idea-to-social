import logging.config
import os
import unittest
from unittest import mock

from test.app.test_functions import init_logging, load_agent_config
from aideas.app.agent.agent_name import AgentName
from aideas.app.agent.translation.translator import Translator

init_logging(logging.config)

class TranslatorTest(unittest.TestCase):
    def test_translate_file_path(self):
        parent_dir = "parent-dir"
        result = self._test_translate_file_path("en", "Hello world", "de", "Hallo Welt", parent_dir)
        expected_result = os.path.join(parent_dir, "Hallo Welt.txt")
        self.assertEqual(result, expected_result)

    def test_translate_file_path_when_filename_not_translated(self):
        parent_dir = "parent-dir"
        text = "Hello world"
        result = self._test_translate_file_path("en", text, "de", text, parent_dir)
        expected_result = os.path.join(parent_dir, f"{text}.de.txt")
        self.assertEqual(result, expected_result)

    @staticmethod
    def _test_translate_file_path(
            from_lang: str, text: str,
            to_lang: str, text_translated: str, parent_dir: str = "parent-dir") -> str:

        with mock.patch.object(Translator, "translate") as translate:
            translate.return_value = text_translated

            translator: Translator = Translator.of_config(load_agent_config(AgentName.TRANSLATION, False))

            input_file_path = os.path.join(parent_dir, f"{text}.txt")
            result = translator.translate_file_path(input_file_path, from_lang, to_lang)

            translate.assert_called_once_with(text, from_lang, to_lang)

            return result


if __name__ == '__main__':
    unittest.main()

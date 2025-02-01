import unittest

from aideas.app.agent.translation.translator import Translator
from test.app.agent.translation.test_translator import TestTranslator


class TranslatorTest(unittest.TestCase):

    def test_translate(self):
        # expected_result = TestTranslator.get_expected_result()
        input_list = TestTranslator.get_input()
        translator = Translator("https://translate.googleapis.com/translate_a/single")
        result = translator.translate(input_list, 'uk', 'en')
        # print(f'Expect: {expected_result}')
        # print(f'Result: {result}')
        # self.assertEqual(expected_result, result)
        self.assertEqual(len(input_list), len(result))
        # Only the first 2 chars i.e. the number may be assured to be same.
        lhs = [e[0:2] for e in input_list]
        rhs = [e[0:2] for e in result]
        self.assertEqual(lhs, rhs)


if __name__ == '__main__':
    unittest.main()

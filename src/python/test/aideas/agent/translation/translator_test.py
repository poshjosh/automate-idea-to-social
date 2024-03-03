import unittest

from .test_translator import TestTranslator


class TranslatorTest(unittest.TestCase):

    def test_translate(self):
        expected_result = TestTranslator.get_expected_result()
        input_list = TestTranslator.get_input()
        translator = TestTranslator("https://translate.googleapis.com/translate_a/single")
        result = translator.translate(input_list, 'uk', 'en')
        #print(f'Result: {result}')
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()

import unittest

from aideas.app.agent.translation.translator import Translator

class TranslatorIT(unittest.TestCase):
    def test_translate(self):
        # Any input more complex than this, may result to inconsistent translations.
        input_list = [
            "1. так.",
            "2. немає.",
        ]
        expected_result = [
            "1. Yes.",
            "2. No."
        ]
        translator = Translator("https://translate.googleapis.com/translate_a/single")
        result = translator.translate(input_list, 'uk', 'en')
        # print(f'Expect: {expected_result}')
        # print(f'Result: {result}')
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()

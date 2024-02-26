import unittest
from unittest.mock import patch

from .....main.aideas.agent.translation.translator import Translator


class TranslatorTest(unittest.TestCase):

    @patch('requests.get')
    def test_translate(self, mock_get):
        mock_res_json = [[['1. My name is Tina and I am a software engineer at Google. ', '1. Мене звати Тіна, я інженер-програміст у Google.', None, None, 3, None, None, [[]], [[['1eb561d2d816b8957a38cd5018eb164c', 'tea_AllEn_2022q2.md']]]], ['And also something here from two sentences. ', 'А також щось тут з двох речень.', None, None, 3, None, None, [[]], [[['1eb561d2d816b8957a38cd5018eb164c', 'tea_AllEn_2022q2.md']]]], ["u~~~u 2. As a software engineer, I work on an internal tool, u~~~u 3. that serves Google's security engineers and network engineers.", 'u~~~u 2. Як інженер-програміст, я працюю над внутрішнім інструментом, u~~~u 3. який обслуговує інженерів безпеки та мережевих інженерів Google.', None, None, 3, None, None, [[]], [[['1eb561d2d816b8957a38cd5018eb164c', 'tea_AllEn_2022q2.md']]]]], None, 'uk', None, None, None, None, []]
        expected_result = ['1. My name is Tina and I am a software engineer at Google. And also something here from two sentences.', '2. As a software engineer, I work on an internal tool,', "3. that serves Google's security engineers and network engineers."]
        mock_response = mock_get.return_value
        mock_response.json.return_value = mock_res_json

        input_list = [
            "1. Мене звати Тіна, я інженер-програміст у Google. А також щось тут з двох речень.",
            "2. Як інженер-програміст, я працюю над внутрішнім інструментом, ",
            "3. який обслуговує інженерів безпеки та мережевих інженерів Google.",
        ]

        translator = Translator("https://test-translation-service")
        result = translator.translate(input_list, 'uk', 'en')
        #print(f'Result: {result}')
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()

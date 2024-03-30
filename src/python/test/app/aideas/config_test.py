import unittest

from ....main.app.aideas.config import tokenize


class ConfigTest(unittest.TestCase):
    def test_of_given_multiple_quotes_should_return_valid_action(self):
        action_signature = 'first " " $VIDEO_TITLE "#shorts"'
        result = tokenize(action_signature)
        self.assertEqual(['first', ' ', '$VIDEO_TITLE', '#shorts'], result)

    def test_tokenize_given_multiple_quote_mixed_with_spaces_should_return_valid_action(self):
        action_signature = 'test-action " a boy shorts" tinkerer'
        result = tokenize(action_signature)
        self.assertEqual(['test-action', ' a boy shorts', 'tinkerer'], result)


if __name__ == '__main__':
    unittest.main()

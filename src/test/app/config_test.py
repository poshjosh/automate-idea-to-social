import copy
import unittest

from aideas.app.config import tokenize, merge_configs, update_config


class ConfigTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.src = {
            'a': {
                'b': {
                    'bool': False,
                    'list': [0, 1],
                    'dict': {
                        'k0': 'v0',
                        'k1': 'v1'
                    }
                }
            },
            'name': 'Jane'
        }
        self.tgt = {
            'a': {
                'b': {
                    'int': 0,
                    'list': [2, 0],
                    'dict': {
                        'k1': 'v1',
                        'k2': 'v2'
                    }
                }
            },
            'gender': 'f'
        }

    def test_merge_configs_given_lists_are_merged(self):
        self._merge_configs(True)

    def test_merge_configs_given_lists_are_not_merged(self):
        self._merge_configs(False)

    def _merge_configs(self, merge_lists: bool):
        src = copy.deepcopy(self.src)
        tgt = copy.deepcopy(self.tgt)

        output = merge_configs(src, tgt, merge_lists)
        print(f"Merge output: {output}")

        self.assertDictEqual(self.src, src)
        self.assertDictEqual(self.tgt, tgt)

        self.assertEqual('f', output.get('gender'))
        self.assertEqual('Jane', output.get('name'))
        b = output.get('a', {}).get('b', {})
        self.assertEqual(0, b.get('int'))
        self.assertFalse(b.get('bool'))
        if merge_lists is True:
            self.assertListEqual([0, 1, 2], b.get('list'))
        else:
            self.assertListEqual([0, 1], b.get('list'))
        self.assertDictEqual({'k0': 'v0', 'k1': 'v1', 'k2': 'v2'}, b.get('dict'))

    def test_update_config(self):
        src = copy.deepcopy(self.src)
        tgt = copy.deepcopy(self.tgt)

        output = update_config(src, tgt)
        #print(f"Update output: {output}")

        self.assertDictEqual(self.src, src)
        self.assertDictEqual(self.tgt, tgt)

        self.assertEqual('f', output.get('gender'))
        self.assertEqual('Jane', output.get('name'))
        b = output.get('a', {}).get('b', {})
        self.assertIsNone(b.get('int'))
        self.assertFalse(b.get('bool'))
        self.assertListEqual([0, 1], b.get('list'))
        self.assertDictEqual({'k0': 'v0', 'k1': 'v1'}, b.get('dict'))

    def test_of_given_multiple_quotes_should_return_valid_action(self):
        action_signature = 'first " " $TEXT_TITLE "#shorts"'
        result = tokenize(action_signature)
        self.assertEqual(['first', ' ', '$TEXT_TITLE', '#shorts'], result)

    def test_tokenize_given_multiple_quote_mixed_with_spaces_should_return_valid_action(self):
        action_signature = 'test-action " a boy shorts" tinkerer'
        result = tokenize(action_signature)
        self.assertEqual(['test-action', ' a boy shorts', 'tinkerer'], result)


if __name__ == '__main__':
    unittest.main()

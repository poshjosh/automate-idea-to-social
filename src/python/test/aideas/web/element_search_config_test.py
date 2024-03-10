import unittest

from ....main.aideas.web.element_search_config import ElementSearchConfig


class ElementSearchConfigTest(unittest.TestCase):
    def test_to_attr_dict_should_succeed_given_single_pair(self):
        k = "name"
        v = "value"
        attr: dict[str, str] = ElementSearchConfig.to_attr_dict(f"{k}={v}")
        self.assertEqual(v, attr[k])

    def test_to_attr_dict_should_resolve_single_pair_with_quotes(self):
        k = "name"
        v = "value with spaces"
        attr: dict[str, str] = ElementSearchConfig.to_attr_dict(f'{k}="{v}"')
        self.assertEqual(v, attr[k])

    def test_to_attr_dict_should_succeed_given_multiple_pairs(self):
        k0 = "name0"
        v0 = "value0"
        k1 = "name0"
        v1 = "value0"
        attr: dict[str, str] = ElementSearchConfig.to_attr_dict(f"{k0}={v0} {k1}={v1}")
        self.assertEqual(v0, attr[k0])
        self.assertEqual(v1, attr[k1])

    def test_to_attr_dict_should_succeed_given_multiple_pairs_with_quotes(self):
        k0 = "name0"
        v0 = "value0 with spaces"
        k1 = "name1"
        v1 = "value1 with spaces"
        attr: dict[str, str] = ElementSearchConfig.to_attr_dict(f'{k0}="{v0}" {k1}="{v1}"')
        self.assertEqual(v0, attr[k0])
        self.assertEqual(v1, attr[k1])

    def test_to_attr_dict_should_fail_given_multiple_pairs_with_misplaced_quotes(self):
        k0 = "name0"
        v0 = "value0 with spaces"
        k1 = "name1"
        v1 = "value1 with spaces"
        self.assertRaises(ValueError, ElementSearchConfig.to_attr_dict, f'{k0}="{v0} {k1}={v1}')

    def test_to_attr_dict_should_fail_given_multiple_pairs_with_misplaced_quote_at_end(self):
        k0 = "name0"
        v0 = "value0 with spaces"
        k1 = "name1"
        v1 = "value1 with spaces"
        self.assertRaises(ValueError, ElementSearchConfig.to_attr_dict, f'{k0}={v0} {k1}={v1}"')


if __name__ == '__main__':
    unittest.main()

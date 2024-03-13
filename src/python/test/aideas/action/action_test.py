import unittest

from ....main.aideas.action.action import Action, NOT

agent_name = "test-agent-name"
stage_id = "test-stage-id"
target_id = "test-target-id"


class ActionTest(unittest.TestCase):
    def test_of_given_no_arg_should_return_valid_action(self):
        expected_name = 'test-action'
        action = Action.of(agent_name, stage_id, target_id, expected_name)
        self.assertFalse(action.is_negation())
        self.assertEqual(expected_name, action.get_name())

    def test_of_given_no_arg_and_negation_should_return_valid_action(self):
        name_without_negation = 'test-action'
        expected_name = f'{NOT} {name_without_negation}'
        action = Action.of(agent_name, stage_id, target_id, expected_name)
        self.assertTrue(action.is_negation())
        self.assertEqual(expected_name, action.get_name())
        self.assertEqual(name_without_negation, action.get_name_without_negation())

    def test_of_given_one_arg_should_return_valid_action(self):
        expected_name = 'test-action'
        expected_arg = 'arg0'
        action_signature = f'{expected_name} {expected_arg}'
        action = Action.of(agent_name, stage_id, target_id, action_signature)
        self.assertFalse(action.is_negation())
        self.assertEqual(expected_name, action.get_name())
        self.assertEqual([expected_arg], action.get_args())

    def test_of_given_multiple_args_should_return_valid_action(self):
        expected_name = 'test-action'
        action_signature = f'{expected_name} arg0 arg1'
        action = Action.of(agent_name, stage_id, target_id, action_signature)
        self.assertFalse(action.is_negation())
        self.assertEqual(expected_name, action.get_name())
        self.assertEqual(['arg0', 'arg1'], action.get_args())

    def test_of_given_multiple_args_and_negation_should_return_valid_action(self):
        expected_name_without_negation = 'test-action'
        expected_name = f'{NOT} {expected_name_without_negation}'
        action_signature = f'{expected_name} arg0 arg1'
        action = Action.of(agent_name, stage_id, target_id, action_signature)
        self.assertTrue(action.is_negation())
        self.assertEqual(expected_name_without_negation, action.get_name_without_negation())
        self.assertEqual(expected_name, action.get_name())
        self.assertEqual(['arg0', 'arg1'], action.get_args())


if __name__ == '__main__':
    unittest.main()

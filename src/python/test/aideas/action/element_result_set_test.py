import unittest

from ....main.aideas.action.action import Action
from ....main.aideas.action.action_result import ActionResult
from ....main.aideas.result.element_result_set import ElementResultSet


class ElementResultSetTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        action_signature = 'wait 0'
        agent = 'test-agent'
        stage = 'test-stage'
        self.success_0 = ActionResult(Action.of(agent, stage, 'success_0', action_signature), True)
        self.success_1 = ActionResult(Action.of(agent, stage, 'success_1', action_signature), True)
        self.failure_0 = ActionResult(Action.of(agent, stage, 'failure_0', action_signature), False)
        self.failure_1 = ActionResult(Action.of(agent, stage, 'failure_1', action_signature), False)

    # We allow duplicate actions, because some stages and their actions may be repeated
    # def test_add_should_fail_given_existing_action(self):
    #     first: ActionResult = self.success_0
    #     copy: ActionResult = ActionResult(first.get_action(), first.is_success(), first.get_result())
    #     self.assertRaises(ValueError, lambda: ActionResultSet().add(first).add(copy))

    def test_add_given_one_failure_after_success_should_be_failure(self):
        result_set = ElementResultSet().add(self.success_0).add(self.failure_0)
        print(result_set)
        self.assertTrue(result_set.is_failure())

    def test_add_given_one_failure_before_success_should_be_failure(self):
        result_set = ElementResultSet().add(self.failure_0).add(self.success_0)
        print(result_set)
        self.assertTrue(result_set.is_failure())

    def test_add_given_no_failure_should_be_success(self):
        result_set = ElementResultSet().add(self.success_0).add(self.success_1)
        print(result_set)
        self.assertTrue(result_set.is_successful())

    def test_add_given_only_failures_should_be_failure(self):
        result_set = ElementResultSet().add(self.failure_0).add(self.failure_1)
        print(result_set)
        self.assertTrue(result_set.is_failure())

    def test_add_after_close_should_fail(self):
        def target():
            ElementResultSet().add(self.success_0).close().add(self.success_1)

        self.assertRaises(ValueError, target)

    def test_add_after_create_from_results_should_increase_size_by_added(self):

        result_set = ElementResultSet().add(self.success_0).add(self.failure_0)
        size_before = result_set.size()
        result_set = result_set.add(self.failure_1)
        size_after = result_set.size()
        print(f'size_before: {size_before}, size_after: {size_after}')
        #print(result_set)
        self.assertEqual(size_before + 1, size_after)


if __name__ == '__main__':
    unittest.main()

import unittest
import uuid
from typing import Union

from aideas.app.action.action import Action
from aideas.app.action.action_result import ActionResult
from aideas.app.result.result_set import ResultSet, ElementResultSet, StageResultSet, AgentResultSet


class Common:
    AGENT_NAME = 'test-agent'
    STAGE_ID = 'test-stage'

    @staticmethod
    def given_success_result(
            stage_item_id="success_stage_item",
            stage_id=STAGE_ID, agent=AGENT_NAME) -> ActionResult:
        return ActionResult.success(Common.given_action(stage_item_id, stage_id, agent))

    @staticmethod
    def given_failure_result(
            stage_item_id="failure_stage_item",
            stage_id=STAGE_ID, agent=AGENT_NAME) -> ActionResult:
        return ActionResult.failure(Common.given_action(stage_item_id, stage_id, agent))

    @staticmethod
    def given_action(stage_item_id: str, stage_id=STAGE_ID, agent=AGENT_NAME) -> Action:
        return Action.of(agent, stage_id, stage_item_id, 'test_action')
    
    class ResultSetTest(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def _create_new(self, results: Union[dict[str, any], None] = None) -> ResultSet:
            raise NotImplementedError("Please implement me")

        def test_add_after_close_should_fail(self):
            result_set = self._create_new().close()
            self.assertRaises(
                ValueError, result_set.add_action_result, Common.given_success_result())

        def test_add_after_create_should_increase_size_by_added(self):
            result_set = self._create_with_results(1, 1)
            size_before = result_set.size()
            result_set = result_set.add_action_result(
                Common.given_success_result(str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())))
            size_after = result_set.size()
            self.assertEqual(size_before + 1, size_after)

        def test_size_given_empty(self):
            self.assertEqual(0, self._create_new().size())

        def test_size_given_not_empty(self):
            self.assertEqual(1, self._create_with_results(1).size())

        def test_is_empty_given_empty(self):
            self.assertTrue(self._create_new().is_empty())

        def test_is_empty_given_not_empty(self):
            self.assertFalse(self._create_with_results(1).is_empty())

        def test_success_count_given_empty(self):
            self.assertEqual(0, self._create_new().success_count())

        def test_success_count_given_some_success(self):
            self.assertEqual(1, self._create_with_results(1, 1).success_count())

        def test_success_count_given_no_success(self):
            self.assertEqual(0, self._create_with_results(0, 1).success_count())

        def test_failure_count_given_empty(self):
            self.assertEqual(0, self._create_new().failure_count())

        def test_failure_count_given_some_failure(self):
            self.assertEqual(1, self._create_with_results(1, 1).failure_count())

        def test_failure_count_given_no_failure(self):
            self.assertEqual(0, self._create_with_results(1, 0).failure_count())

        def test_is_failure_given_empty(self):
            self.assertTrue(self._create_new().is_failure())

        def test_is_failure_given_some_failure(self):
            self.assertTrue(self._create_with_results(1, 1).is_failure())

        def test_is_failure_given_no_failure(self):
            self.assertFalse(self._create_with_results(1, 0).is_failure())

        def test_is_successful_given_empty(self):
            self.assertFalse(self._create_new().is_successful())

        def test_is_successful_given_some_success(self):
            self.assertFalse(self._create_with_results(1, 1).is_successful())

        def test_is_successful_given_no_success(self):
            self.assertFalse(self._create_with_results(0, 1).is_successful())

        def test_init_is_equivalent_to_set(self):
            results = {**self._create_with_results(1, 1).results()}
            lhs = self._create_new(results)
            rhs = self._create_new()
            for key, value in results.items():
                rhs.set(key, value)

            self.assertEqual(lhs, rhs)

        def _create_with_results(self, success_count: int = 0, failure_count: int = 0) -> ResultSet:
            result_set = self._create_new()

            for i in range(success_count):
                result_set.add_action_result(
                    Common.given_success_result(f"success_stage_item_{i}", f"stage_{i}"))

            size = result_set.size()
            # We add the size to the index below because, we want multiple stages i.e. this:
            #
            # stage_0
            #     success_stage_item_0
            #         ActionResult(success=True, Action(success_stage_item_0.test_action[]), result=None)
            # stage_1
            #     failure_stage_item_0
            #         ActionResult(success=False, Action(failure_stage_item_0.test_action[]), result=None)
            #
            # Not a single stage, i.e. this:
            #
            # stage_0
            #     failure_stage_item_0
            #         ActionResult(success=False, Action(failure_stage_item_0.test_action[]), result=None)
            #     success_stage_item_0
            #         ActionResult(success=True, Action(success_stage_item_0.test_action[]), result=None)

            for i in range(failure_count):
                result_set.add_action_result(
                    Common.given_failure_result(f"failure_stage_item_{i}", f"stage_{i + size}", f"agent_{i + size}"))

            return result_set


class ElementResulSetTest(Common.ResultSetTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_new(self, results: Union[dict[str, any], None] = None) -> ElementResultSet:
        return ElementResultSet(results)

    def test_init_is_equivalent_to_add(self):
        result_list = [Common.given_success_result(), Common.given_failure_result()]
        results = {}
        for result in result_list:
            results[result.get_action().get_stage_item_id()] = [result]

        lhs = self._create_new(results)
        rhs = self._create_new()
        for result in result_list:
            rhs.add_action_result(result)

        self.assertEqual(lhs, rhs)


class StageResulSetTest(Common.ResultSetTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_new(self, results: Union[dict[str, any], None] = None) -> StageResultSet:
        return StageResultSet(results)


class AgentResulSetTest(Common.ResultSetTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_new(self, results: Union[dict[str, any], None] = None) -> AgentResultSet:
        return AgentResultSet(results)

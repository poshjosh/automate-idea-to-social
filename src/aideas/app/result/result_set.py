from collections import OrderedDict
from collections.abc import Iterable
import copy
import logging
from typing import Union, TypeVar, Callable

from ..action.action_result import ActionResult

logger = logging.getLogger(__name__)

RESULT = TypeVar('RESULT', bound=any)


####################################################################################################
# DO NOT ARBITRARILY MODIFY THIS CLASS
# IT IS SERIALIZED, AND WILL BE DESERIALIZED FOR USE
####################################################################################################


class ResultSet:
    def __init__(self,
                 success_test: Callable[[RESULT], bool],
                 results: Union[dict[str, RESULT], None] = None):
        self.__closed = False
        if success_test is None:
            raise ValueError('success_test cannot be None')
        self.__success_test = success_test
        self.__results: OrderedDict[str, RESULT] = OrderedDict()
        if results is not None:
            self.__results.update(copy.deepcopy(results))

    def add_action_result(self, result: ActionResult) -> 'ResultSet':
        raise NotImplementedError('Please implement me')

    def get(self, result_id: str, result_if_none: RESULT = None) -> RESULT:
        """Returns a copy of the result or the result_if_none when the result is not found."""
        return self.__get(result_id, result_if_none)

    def keys(self) -> set[str]:
        return set(self.__results.keys())

    def values(self) -> list[RESULT]:
        return [e for e in self.__results.values()]

    def set_all(self, result_set: 'ResultSet') -> 'ResultSet':
        for key, result in result_set.__results.items():
            self.set(key, result)
        return self

    def set(self, key: str, value: RESULT) -> 'ResultSet':
        self.__set(key, value)
        return self

    def __get(self, result_id: str, result_if_none: RESULT = None) -> RESULT:
        return self.__results.get(result_id, result_if_none)

    def __set(self, result_id: str, value: RESULT) -> RESULT:
        self.__required_not_closed()
        if value is None:
            raise ValueError('Cannot add None')
        if result_id in self.__results:
            raise ValueError(f'Already added: {result_id}')

        existing = self.__results.get(result_id, None)
        self.__results[result_id] = value
        return existing

    def close(self) -> 'ResultSet':
        self.__closed = True
        for result in self.__results.values():
            if isinstance(result, ResultSet):
                result.close()
        return self

    def is_empty(self) -> bool:
        return self.size() == 0

    def size(self) -> int:
        return len(self.__results)

    def is_successful(self) -> bool:
        return self.size() > 0 and self.failure_count() == 0

    def is_failure(self) -> bool:
        return not self.is_successful()

    def success_count(self) -> int:
        return self.size() - self.failure_count()

    def failure_count(self) -> int:
        failures: int = 0
        for result in self.__results.values():
            if not self.__success_test(result):
                failures += 1
        return failures

    def items(self):
        return self.__results.items()

    def results(self):
        return self.__results

    def pretty_str(self, separator: str = "\n", tab: str = "\t", offset: int = 0) -> str:
        output: str = ''
        for key in self.keys():
            output = f'{output}{separator}{tab * offset}{key}'
            value = self.get(key)
            if isinstance(value, ResultSet):
                output = f'{output}{value.pretty_str(separator, tab, offset + 1)}'
            elif isinstance(value, dict):
                for k, v in value.items():
                    output = f'{output}{separator}{tab * (offset + 1)}{k}={v}'
            elif isinstance(value, Iterable):
                for e in value:
                    output = f'{output}{separator}{tab * (offset + 1)}{e}'
            else:
                output = f'{output}{separator}{tab * (offset + 1)}{value}'
        return output

    def __required_not_closed(self):
        if self.__closed:
            raise ValueError('Cannot update result set when closed')

    def __eq__(self, other) -> bool:
        return self.__closed == other.__closed and self.__results == other.__results

    def __str__(self) -> str:
        return f'ResultSet(success-rate={self.success_count()}/{self.size()})'


class ElementResultSet(ResultSet):
    @staticmethod
    def none() -> 'ElementResultSet':
        return NOOP_ELEMENT_RESULT_SET

    def __init__(self, results: Union[dict[str, list[ActionResult]], None] = None):
        super().__init__(self.is_result_successful, results)

    def add_action_result(self, result: ActionResult) -> 'ElementResultSet':
        stage_item_id: str = result.get_action().get_stage_item_id()
        result_list: list[ActionResult] = self.get(stage_item_id, [])
        result_list.append(result)
        # We only set if the list is newly created, otherwise an exception will be thrown
        if len(result_list) == 1:
            self.set(stage_item_id, result_list)
        return self

    def get_action_result(self,
                          stage_item_id: str,
                          action_name: str,
                          result_if_none: Union[ActionResult, None] = None) -> ActionResult:
        result_list: list[ActionResult] = self.get(stage_item_id)
        if len(result_list) == 0:
            return result_if_none
        for result in result_list:
            if result.get_action().get_name() == action_name:
                return result
        return result_if_none

    @staticmethod
    def is_result_successful(result: list[ActionResult]) -> bool:
        for r in result:
            if r.is_success() is False:
                return False
        return True


NOOP_ELEMENT_RESULT_SET: ElementResultSet = ElementResultSet().close()


class StageResultSet(ResultSet):
    @staticmethod
    def none() -> 'StageResultSet':
        return NOOP_STAGE_RESULT_SET

    def __init__(self, results: Union[dict[str, ElementResultSet], None] = None):
        super().__init__(self.is_result_successful, results)

    @staticmethod
    def is_result_successful(result: ElementResultSet) -> bool:
        return result.is_successful()

    def add_action_result(self, result: ActionResult) -> 'StageResultSet':
        stage_id = result.get_action().get_stage_id()
        new_stage_element = False
        element_result_set: ElementResultSet = self.get(stage_id, None)
        if element_result_set is None:
            new_stage_element = True
            element_result_set = ElementResultSet()
        element_result_set.add_action_result(result)
        if new_stage_element:
            self.set(stage_id, element_result_set)
        return self

    def get_element_results(self,
                            stage_id: str,
                            result_if_no: Union[ElementResultSet, None] = ElementResultSet.none()) \
            -> ElementResultSet:
        return self.get(stage_id, result_if_no)


NOOP_STAGE_RESULT_SET: StageResultSet = StageResultSet().close()


class AgentResultSet(ResultSet):
    def __init__(self, results: Union[dict[str, StageResultSet], None] = None):
        super().__init__(self.is_result_successful, results)

    @staticmethod
    def is_result_successful(result: ResultSet) -> bool:
        return result.is_successful()

    def add_action_result(self, result: ActionResult) -> 'AgentResultSet':
        agent_name = result.get_action().get_agent_name()
        new_stage = False
        stage_result_set: StageResultSet = self.get_stage_results(agent_name, None)
        if stage_result_set is None:
            new_stage = True
            stage_result_set = StageResultSet()
        stage_result_set.add_action_result(result)
        if new_stage:
            self.set(agent_name, stage_result_set)
        return self

    def get_element_results(self,
                            agent_name: str,
                            stage_id: str,
                            result_if_no: Union[ElementResultSet, None] = ElementResultSet.none()) \
            -> ElementResultSet:
        stage_result_set: StageResultSet = self.get_stage_results(agent_name)
        return result_if_no if stage_result_set is None \
            else stage_result_set.get_element_results(stage_id, result_if_no)

    def get_stage_results(self,
                          agent_name: str,
                          result_if_none: Union[StageResultSet, None] = StageResultSet.none()) \
            -> StageResultSet:
        return self.get(agent_name, result_if_none)

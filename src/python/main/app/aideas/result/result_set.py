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
        self.__results: dict[str, RESULT] = {}
        if results is not None:
            self.__results.update(copy.deepcopy(results))

    """Returns a copy of the result or the result_if_none if the result is not found."""
    def get(self, result_id: str, result_if_none: RESULT = None) -> RESULT:
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
        self.__check_closed()
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

    def is_successful(self):
        return self.size() > 0 and self.__count_failures() == 0

    def is_failure(self):
        return not self.is_successful()

    def items(self):
        return self.__results.items()

    def pretty_str(self, separator: str = "\n", offset: int = 0) -> str:
        tab = '\t'
        output: str = ''
        for key in self.keys():
            output = f'{output}{separator}{tab * offset}{key}'
            value = self.get(key)
            if isinstance(value, ResultSet):
                output = f'{output}{value.pretty_str(separator, offset + 1)}'
            elif isinstance(value, dict):
                for k, v in value.items():
                    output = f'{output}{separator}{tab * (offset + 1)}{k}={v}'
            elif isinstance(value, Iterable):
                for e in value:
                    output = f'{output}{separator}{tab * (offset + 1)}{e}'
            else:
                output = f'{output}{separator}{tab * (offset + 1)}{value}'
        return output

    def __count_failures(self) -> int:
        failures: int = 0
        for result in self.__results.values():
            if not self.__success_test(result):
                failures += 1
        return failures

    def __check_closed(self):
        if self.__closed:
            raise ValueError('Cannot update result set when closed')

    def __eq__(self, other) -> bool:
        return self.__closed == other.__closed and self.__results == other.__results

    def __str__(self) -> str:
        size: int = self.size()
        success: int = size - self.__count_failures()
        return f'ResultSet(success-rate={success}/{size})'


class ElementResultSet(ResultSet):
    @staticmethod
    def none() -> 'ElementResultSet':
        return NOOP_ELEMENT_RESULT_SET

    def __init__(self, results: Union[dict[str, list[ActionResult]], None] = None):
        super().__init__(self.is_result_successful, results)

    def add_all(self, result_set: 'ElementResultSet') -> 'ElementResultSet':
        for result_list in result_set.values():
            for result in result_list:
                self.add(result)
        return self

    def add(self, result: ActionResult) -> 'ElementResultSet':
        target_id: str = result.get_action().get_target_id()
        result_list: list[ActionResult] = self.get(target_id, [])
        result_list.append(result)
        # We only set if the list is newly created, otherwise an exception will be thrown
        if len(result_list) == 1:
            self.set(target_id, result_list)
        return self

    def get_action_result(self,
                          target_id: str,
                          name: str,
                          result_if_none: Union[ActionResult, None] = None) -> ActionResult:
        result_list: list[ActionResult] = self.get(target_id)
        if len(result_list) == 0:
            return result_if_none
        for result in result_list:
            if result.get_action().get_name() == name:
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


NOOP_STAGE_RESULT_SET: StageResultSet = StageResultSet().close()


class AgentResultSet(ResultSet):
    def __init__(self, results: Union[dict[str, StageResultSet], None] = None):
        super().__init__(self.is_result_successful, results)

    @staticmethod
    def is_result_successful(result: StageResultSet) -> bool:
        return result.is_successful()

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
                 results: Union[dict[str, RESULT], None] = None,
                 total: int = 0,
                 failure: int = 0):
        self.__closed = False
        if success_test is None:
            raise ValueError('success_test cannot be None')
        self.__success_test = success_test
        self.__results: dict[str, RESULT] = {}
        if results is not None:
            self.__results.update(copy.deepcopy(results))
        self.__total = total
        self.__failure = failure

    """Returns a copy of the result or the result_if_none if the result is not found."""
    def get(self, result_id: str, result_if_none: RESULT = None) -> RESULT:
        return self.__get(result_id, result_if_none)

    def keys(self) -> set[str]:
        return set(self.__results.keys())

    def values(self) -> set[RESULT]:
        return set(self.__results.values())

    def set_all(self, result_set: 'ResultSet') -> 'ResultSet':
        for key, result in result_set.__results.items():
            self.set(key, result)
        return self

    def set(self, key: str, value: RESULT) -> 'ResultSet':
        self.__set(key, value)
        self.__total += 1
        if not self.__success_test(value):
            self.__failure += 1
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
        return self.__total

    def is_successful(self):
        return self.__failure == 0 and self.size() > 0

    def is_failure(self):
        return self.__failure > 0

    def items(self):
        return self.__results.items()

    def get_total(self) -> int:
        return self.__total

    def get_failure(self) -> int:
        return self.__failure

    def __eq__(self, other) -> bool:
        return self.__closed == other.__closed and self.__results == other.__results

    def __str__(self) -> str:
        success: int = self.__total - self.__failure
        return f'ResultSet(success-rate={success}/{self.__total})'

    def __check_closed(self):
        if self.__closed:
            raise ValueError('Cannot update result set when closed')


class ElementResultSet(ResultSet):
    @staticmethod
    def none() -> 'ElementResultSet':
        return NOOP_ELEMENT_RESULT_SET

    def __init__(self,
                 results: Union[dict[str, list[ActionResult]], None] = None,
                 total: int = 0,
                 failure: int = 0):
        super().__init__(self.is_result_successful, results, total, failure)

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

    def is_result_successful(self, result: list[ActionResult]) -> bool:
        for r in result:
            if not r.is_success():
                return False
        return True

    def pretty_str(self, separator: str = "\n", offset: int = 0) -> str:
        tab = '\t'
        output: str = ''
        for elem in self.keys():
            output = f'{output}{separator}{tab * offset}{elem}'
            action_results = self.get(elem)
            for action_result in action_results:
                output = f'{output}{separator}{tab * (offset + 1)}{action_result}'
        return output


NOOP_ELEMENT_RESULT_SET: ElementResultSet = ElementResultSet().close()


class StageResultSet(ResultSet):
    @staticmethod
    def none() -> 'StageResultSet':
        return NOOP_STAGE_RESULT_SET

    def __init__(self,
                 results: Union[dict[str, ElementResultSet], None] = None,
                 total: int = 0,
                 failure: int = 0):
        super().__init__(self.is_result_successful, results, total, failure)

    def is_result_successful(self, result: ElementResultSet) -> bool:
        return result.is_successful()

    def pretty_str(self, separator: str = "\n", offset: int = 0) -> str:
        tab = '\t'
        output: str = ''
        for stage in self.keys():
            output = f'{output}{separator}{tab * offset}{stage}'
            element_results = self.get(stage)
            output = f'{output}{element_results.pretty_str(separator, offset + 1)}'
        return output


NOOP_STAGE_RESULT_SET: StageResultSet = StageResultSet().close()


class AgentResultSet(ResultSet):
    def __init__(self,
                 results: Union[dict[str, StageResultSet], None] = None,
                 total: int = 0,
                 failure: int = 0):
        super().__init__(self.is_result_successful, results, total, failure)

    def is_result_successful(self, result: StageResultSet) -> bool:
        return result.is_successful()

    def pretty_str(self, separator: str = "\n", offset: int = 0) -> str:
        tab = '\t'
        output: str = ''
        for stage in self.keys():
            output = f'{output}{separator}{tab * offset}{stage}'
            stage_results = self.get(stage)
            output = f'{output}{stage_results.pretty_str(separator, offset + 1)}'
        return output

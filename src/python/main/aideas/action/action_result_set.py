import copy
import logging
from typing import Union

from .action_result import ActionResult

logger = logging.getLogger(__name__)


class ActionResultSet:
    @staticmethod
    def none() -> 'ActionResultSet':
        return NO_EXECUTION

    def __init__(self,
                 results: Union[dict[str, list[ActionResult]], None] = None,
                 total: int = 0,
                 failure: int = 0):
        self.__closed = False
        self.__results: dict[str, list[ActionResult]] = {}
        if results is not None:
            self.__results.update(copy.deepcopy(results))
        self.__total = total
        self.__failure = failure

    def create_from_results(self) -> 'ActionResultSet':
        return ActionResultSet(self.__results, self.__total, self.__failure)

    def add_all(self, result_set: 'ActionResultSet') -> 'ActionResultSet':
        for result_list in result_set.__results.values():
            for result in result_list:
                self.add(result)
        return self

    def add(self, result: ActionResult) -> 'ActionResultSet':
        if self.__closed:
            raise ValueError('Result is closed')
        target_id: str = result.get_action().get_target_id()
        result_list: list[ActionResult] = self.__get(target_id)
        # We allow duplicate actions, because some stages and their actions may be repeated
        # for res in result_list:
        #     if res.get_action() == result.get_action():
        #         raise ValueError(f"Already added: {result}")
        result_list.append(result)
        self.__set(target_id, result_list)
        self.__total += 1
        if result.is_success() is False:
            self.__failure += 1
        return self

    def get_action_result(self,
                          target_id: str,
                          name: str,
                          result_if_none: Union[ActionResult, None] = None) -> ActionResult:
        result_list: list[ActionResult] = self.__get(target_id)
        if len(result_list) == 0:
            return result_if_none
        for result in result_list:
            if result.get_action().get_name() == name:
                return result
        return result_if_none

    def get(self, target_id: str) -> list[ActionResult]:
        return list(self.__get(target_id))

    def keys(self) -> list[str]:
        return list(self.__results.keys())

    def pretty_str(self, separator: str = "\n") -> str:
        return separator.join(f'{k}: {self.__deep_str(v)}' for k,v in self.__results.items())

    def __deep_str(self, what: list):
        str_list: list[str] = []
        for e in what:
            str_list.append(str(e))
        return ' '.join(str_list)

    def __get(self, target_id: str) -> list[ActionResult]:
        return self.__results.get(target_id, [])

    def __set(self, target_id: str, value: list[ActionResult]):
        if value is None:
            raise ValueError('Value cannot be None')
        self.__results[target_id] = value

    def close(self) -> 'ActionResultSet':
        self.__closed = True
        return self

    def is_empty(self) -> bool:
        return self.size() == 0

    def size(self) -> int:
        return self.__total

    def is_successful(self):
        return self.__failure == 0 and self.size() > 0

    def is_failure(self):
        return self.__failure > 0

    def __eq__(self, other) -> bool:
        return self.__closed == other.__closed and self.__results == other.__results

    def __str__(self) -> str:
        success: int = self.__total - self.__failure
        return f'ActionResultSet(success-rate={success}/{self.__total})'


NO_EXECUTION: ActionResultSet = ActionResultSet().close()

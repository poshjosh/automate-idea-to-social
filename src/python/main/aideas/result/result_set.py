import copy
import logging
from typing import Union, TypeVar, Callable

logger = logging.getLogger(__name__)

RESULT = TypeVar('RESULT', bound=any)


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
    
import logging
from typing import Union

from ..action.action_result import ActionResult
from .result_set import ResultSet

logger = logging.getLogger(__name__)


class ElementResultSet(ResultSet):
    @staticmethod
    def none() -> 'ElementResultSet':
        return NONE

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


NONE: ElementResultSet = ElementResultSet().close()

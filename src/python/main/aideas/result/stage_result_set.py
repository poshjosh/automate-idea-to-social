from typing import Union

from .result_set import ResultSet
from .element_result_set import ElementResultSet


class StageResultSet(ResultSet):
    @staticmethod
    def none() -> 'StageResultSet':
        return NONE

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


NONE: StageResultSet = StageResultSet().close()

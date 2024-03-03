from enum import Enum
from typing import TypeVar, Union

T = TypeVar("T", bound=Union[str, dict])


class SearchBy(Enum):
    XPATH = 'search-x-paths'
    SHADOW_ATTRIBUTE = 'search-shadow-attr'


class ElementSearchConfig:
    @staticmethod
    def to_attr(value: str) -> (str, str):
        parts = value.split(' ')
        return parts[0], ' '.join(parts[1:])

    @staticmethod
    def of(config: T) -> 'ElementSearchConfig':
        if type(config) is str:
            search_from = None
            search_for = [str(config)]
            search_by = SearchBy.XPATH
        elif type(config) is dict:
            # Below is a valid stage item (notice it has no xpath).
            #
            # stage-0:
            #   stage-item-0:
            #     action: wait 5
            search_config = config.get(SearchBy.SHADOW_ATTRIBUTE.value)
            if search_config is None:
                search_by = SearchBy.XPATH
                search_config = config.get(SearchBy.XPATH.value)
            else:
                search_by = SearchBy.SHADOW_ATTRIBUTE

            if search_config is None:
                return None
            elif type(search_config) is str:
                search_from = None
                search_for = [search_config]
            elif type(search_config) is list:
                search_from = None
                search_for = search_config
            elif type(search_config) is dict:
                search_from = dict(search_config)['search-from']
                search_for = dict(search_config)['search-for']  # str | list
            else:
                raise ValueError(f'Invalid search config: {config}')
        else:
            raise ValueError(f'Invalid search config: {config}')
        return ElementSearchConfig(search_from, search_for, search_by)

    def __init__(self,
                 search_from: str,
                 search_for: Union[str, list[str]],
                 search_by: SearchBy = SearchBy.XPATH):
        self.__search_from = search_from
        self.__search_for = [search_for] if type(search_for) is str else search_for
        self.__search_by = search_by

    def get_search_from(self) -> str:
        return self.__search_from

    def get_search_for(self) -> [str]:
        return self.__search_for

    def get_search_by(self) -> SearchBy:
        return self.__search_by

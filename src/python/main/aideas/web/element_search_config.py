from enum import Enum
from typing import TypeVar, Union

T = TypeVar("T", bound=Union[str, dict])


class SearchBy(Enum):
    XPATH = 'search-x-paths'
    SHADOW_ATTRIBUTE = 'search-shadow-attributes'


class ElementSearchConfig:
    @staticmethod
    def to_attr_dict(value: str) -> dict[str, str]:
        """
        Converts a string to a dictionary of attributes.
        Input: key_0=value_0 key_1="value with spaces"
        Output: {key_0: value_0, key_1: value with spaces}
        :param value: The value to parse into a dictionary.
        :return: The dictionary of attributes.
        """
        separator = ' '
        value = value.replace('=', separator)
        quote = '"'
        parts = value.split(separator)
        result = []
        sub = []
        for i in range(len(parts)):
            part = parts[i]
            if part.startswith(quote):
                if i == 0:
                    raise ValueError(f'Attribute name cannot have quotes: {part}')
                sub.append(part[1:])
                continue
            if part.endswith(quote):
                if len(sub) == 0:
                    raise ValueError(f'Wrongly placed quote in: {part}')
                sub.append(part[:-1])
                result.append(separator.join(sub))
                sub = []
                continue
            if len(sub) > 0:
                sub.append(part)
                continue
            result.append(part)

        if len(sub) > 0:
            raise ValueError(f'Unmatched quote: {quote}{sub[0]}')

        k = None
        pairs = {}
        for i in range(len(result)):
            if not k:
                k = result[i]
            else:
                pairs[k] = result[i]
                k = None
        return pairs

    @staticmethod
    def of(config: T) -> 'ElementSearchConfig':
        if isinstance(config, str):
            search_from = None
            search_for = [str(config)]
            search_by = SearchBy.XPATH
        elif isinstance(config, dict):
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
            elif isinstance(search_config, str):
                search_from = None
                search_for = [search_config]
            elif isinstance(search_config, list):
                search_from = None
                search_for = search_config
            elif isinstance(search_config, dict):
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

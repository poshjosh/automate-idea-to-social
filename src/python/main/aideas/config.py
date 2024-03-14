import logging
from enum import Enum
from typing import Union, TypeVar

logger = logging.getLogger(__name__)


class Name:
    @staticmethod
    def of(name: Union[str, 'Name'], identifier: Union[str, None] = None) -> 'Name':
        if isinstance(name, Name):
            return name
        return Name(name, identifier)

    @staticmethod
    def of_lists(names: list[str], aliases: Union[list[str], None] = None) -> ['Name']:
        if aliases is not None and len(names) != len(aliases):
            raise ValueError("The number of names and aliases must be the same")
        if aliases is None:
            aliases: [str] = [name for name in names]
        return [Name(names[i], aliases[i]) for i in range(len(names))]

    def __init__(self, name: str, identifier: Union[str, None] = None):
        if name is None:
            raise ValueError('name cannot be None')
        self.__value = name
        self.__id = name if identifier is None else identifier

    def get_id(self) -> str:
        return self.__id

    def get_value(self) -> str:
        return self.__value

    def __eq__(self, other) -> bool:
        return self.__value == other.value and self.__id == other.__id

    def __hash__(self) -> int:
        return hash(self.__value) + hash(self.__id)

    def __str__(self) -> str:
        return self.__value if self.__value == self.__id else f'({self.__value}|{self.__id})'


class ConfigPath(tuple[Name]):
    @staticmethod
    def of(stage: Union[str, Name], stage_item: Union[str, Name] = None) -> 'ConfigPath':
        path = [Name.of(STAGES_KEY), Name.of(stage)]
        if not stage_item:
            return ConfigPath(path)
        path.append(Name.of(STAGE_ITEMS_KEY))
        path.append(Name.of(stage_item))
        return ConfigPath(path)

    def with_appended(self, name: Union[str, Name]) -> 'ConfigPath':
        return ConfigPath([e for e in self] + [Name.of(name)])

    def stage(self) -> Name:
        return self[1]

    def stage_item(self) -> Name:
        return self[3]

    def name(self) -> Name:
        return self[-1]

    def __str__(self) -> str:
        return f'@{".".join([str(e) for e in self])}'


SEARCH_CONFIG_PARENT = TypeVar("SEARCH_CONFIG_PARENT", bound=Union[str, dict])


class SearchBy(Enum):
    XPATH = 'search-x-paths'
    SHADOW_ATTRIBUTE = 'search-shadow-attributes'


class SearchConfig:
    @staticmethod
    def of(config: SEARCH_CONFIG_PARENT) -> Union['SearchConfig', None]:
        if isinstance(config, str):
            search_from = None
            search_for = [str(config)]
            search_by = SearchBy.XPATH
        elif isinstance(config, dict):
            search_config = SearchConfig.__get_search_config(config)
            search_by = SearchConfig.__get_search_by(config)

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
        return SearchConfig(search_from, search_for, search_by)

    @staticmethod
    def __get_search_config(config: SEARCH_CONFIG_PARENT):
        search_config = config.get(SearchBy.SHADOW_ATTRIBUTE.value)
        return config.get(SearchBy.XPATH.value) if search_config is None else search_config

    @staticmethod
    def __get_search_by(config: SEARCH_CONFIG_PARENT):
        search_config = config.get(SearchBy.SHADOW_ATTRIBUTE.value)
        return SearchBy.XPATH if search_config is None else SearchBy.SHADOW_ATTRIBUTE

    def __init__(self,
                 search_from: str,
                 search_for: Union[str, list[str]],
                 search_by: SearchBy = SearchBy.XPATH):
        self.__search_from = search_from
        self.__search_for = [search_for] if isinstance(search_for, str) else search_for
        self.__search_by = search_by
        self.__successful_query_index = -1

    def get_search_from(self) -> str:
        return self.__search_from

    def get_search_for(self) -> [str]:
        return self.__search_for

    def get_search_by(self) -> SearchBy:
        return self.__search_by

    def search_for_needs_reordering(self) -> bool:
        return self.__successful_query_index > 0

    def reorder_search_for(self) -> [str]:
        result = [e for e in self.__search_for]
        if self.__successful_query_index < 1:
            return result
        result.insert(0, result.pop(self.__successful_query_index))
        return result

    def set_successful_query_index(self, index: int):
        self.__successful_query_index = index


STAGES_KEY: str = "stages"
STAGE_ITEMS_KEY: str = "stage-items"
WHEN_KEY: str = 'when'
DEFAULT_ACTIONS_KEY: str = 'default-actions'
TIMEOUT_KEY: str = 'wait-timeout-seconds'

VALUE = TypeVar("VALUE", bound=Union[any, None])


class AgentConfig:
    @staticmethod
    def is_default_actions_key(stage_item: Union[str, Name]) -> bool:
        return AgentConfig.__value(stage_item) == DEFAULT_ACTIONS_KEY

    def __init__(self, config: dict[str, any]):
        self.__config = config

    def root(self) -> dict[str, any]:
        return self.__config

    def stages(self, result_if_none=Union[dict[str, any], None]) -> Union[dict[str, any], None]:
        return self.__config.get(STAGES_KEY, result_if_none)

    def get_stage_names(self) -> [Name]:
        return Name.of_lists(list(self.stages().keys()))

    def stage(self, stage: Union[str, Name], result_if_none=None) -> any:
        return self.stages().get(self.__value(stage), result_if_none)

    def stage_items(self, stage: Union[str, Name], result_if_none=None) -> any:
        """
            #################################
            #   stage-items config format   #
            #################################
            # default-actions: # optional
            #   - click
            #   - wait 2
            # element-0: //*[@id="element-0"]
            # element-1: //*[@id="element-1"]
        """
        return self.stage(self.__value(stage), {}).get(STAGE_ITEMS_KEY, result_if_none)

    def stage_item_names(self, stage: Union[str, Name]) -> [str]:
        stage_items = self.stage_items(stage)
        if not stage_items:
            return []
        result = []
        for name in stage_items.keys():
            if not self.is_default_actions_key(name):
                result.append(name)
        return result

    def stage_item(
            self, stage: Union[str, Name], item: Union[str, Name], result_if_none=None) -> any:
        return self.stage_items(stage, {}).get(self.__value(item), result_if_none)

    def search(
            self, stage: Union[str, Name], stage_item: Union[str, Name]) -> dict[str, any] or None:
        search_config_parent: SEARCH_CONFIG_PARENT = self.__search_parent(stage, stage_item)
        if not isinstance(search_config_parent, dict):
            return None
        search_by_list: [str] = [e.value for e in SearchBy]
        for search_by in search_by_list:
            search_config = search_config_parent.get(search_by)
            if search_config is not None:
                return search_config
        return None

    def get_url(
            self, stage: Union[str, Name], result_if_none: Union[str, None]) -> Union[str, None]:
        return self.stage(stage, {}).get('url', result_if_none)

    def get_depends_on(self) -> [str]:
        return self.__config.get('depends-on', [])

    def get_stage_wait_timeout(self, stage: Union[str, Name], result_if_none: int = 0) -> int:
        return self.get_stage_value(stage, TIMEOUT_KEY, result_if_none)

    def get_stage_value(
            self, stage: Union[str, Name], key: str, result_if_none: VALUE = 0) -> VALUE:
        return self.stage(stage, {}).get(key, result_if_none)

    def get_stage_item_wait_timeout(
            self, stage: Union[str, Name], item: Union[str, Name], result_if_none: int = 0) -> int:
        return self.get_stage_item_value(stage, item, TIMEOUT_KEY, result_if_none)

    def get_stage_item_value(self,
                             stage: Union[str, Name],
                             item: Union[str, Name],
                             key: str,
                             result_if_none: VALUE = 0) -> VALUE:
        return self.stage_item(stage, item, {}).get(key, result_if_none)

    def get_expected(self,
                     path: Union[str, list[str], list[Name], tuple[Name]],
                     result_if_none: Union[str, list, None] = None) -> Union[str, list, None]:
        return self.get(path, {}).get('expected', result_if_none)

    def get(self, path: Union[str, list[str], list[Name], tuple[Name]], result_if_none=None) -> any:
        path: [str] = self.__value_list(path)
        result = self.__config
        for k in path:
            result = result.get(k, None)
            if result is None:
                break
        return result if result else result_if_none

    def __search_parent(
            self, stage: Union[str, Name], stage_item: Union[str, Name]) -> SEARCH_CONFIG_PARENT:
        stage: str = self.__value(stage)
        stage_item: str = self.__value(stage_item)
        if not stage_item:
            return self.stage(stage, None)
        else:
            return self.stage_item(stage, stage_item, None)

    @staticmethod
    def __value_list(path: Union[str, list[str], list[Name], tuple[Name]]) -> [str]:
        if isinstance(path, str):
            return [path]
        result = []
        for e in path:
            result.append(AgentConfig.__value(e))
        return result

    @staticmethod
    def __value(name: Union[str, Name]) -> Union[str, None]:
        return None if name is None else Name.of(name).get_value()


def tokenize(value: str, separator: str = ' ') -> list[str]:
    """
    Converts a string to a dictionary of attributes.
    Input: key_0=value_0 key_1="value with spaces"
    Output: {key_0: value_0, key_1: value with spaces}
    :param value: The value to parse into a dictionary.
    :param separator: The separator between the attributes.
    :return: The dictionary of attributes.
    """
    quote = '"'
    parts = value.split(separator)
    result = []
    sub = []
    for i in range(len(parts)):
        part = parts[i]
        if len(sub) == 0 and part.startswith(quote):
            if i == 0:
                raise ValueError(f'Initial token cannot have quotes: {part}')
            if part.endswith(quote) and part != quote:
                sub.append(part[1:-1])
                result.append(separator.join(sub))
                sub = []
            else:
                sub.append(part[1:])
            continue
        if part.endswith(quote):
            if len(sub) == 0:
                raise ValueError(f'Wrongly placed quote in: {part}')
            if part != quote:
                sub.append(part[:-1])
                result.append(separator.join(sub))
            else:
                result.append(separator)
            sub = []
            continue
        if len(sub) > 0:
            sub.append(part)
            continue
        result.append(part)

    if len(sub) > 0:
        raise ValueError(f'Unmatched quote: {quote}{sub[0]}')

    return result


def __list_to_dict(result: list) -> dict:
    k = None
    pairs = {}
    for i in range(len(result)):
        if not k:
            k = result[i]
        else:
            pairs[k] = result[i]
            k = None
    return pairs


def parse_attributes(value: str) -> dict[str, str]:
    """
    Converts a string to a dictionary of attributes.
    Input: key_0=value_0 key_1="value with spaces"
    Output: {key_0: value_0, key_1: value with spaces}
    :param value: The value to parse into a dictionary.
    :return: The dictionary of attributes.
    """
    separator = ' '
    value = value.replace('=', separator)
    result: list[str] = tokenize(value, separator)
    return __list_to_dict(result)

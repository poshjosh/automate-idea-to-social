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

    def join(self, name: Union[str, Name]) -> 'ConfigPath':
        return ConfigPath([e for e in self] + [Name.of(name)])

    def is_stage(self) -> bool:
        return len(self) == 2

    def is_stage_item(self) -> bool:
        return len(self) == 4

    def stage(self) -> Name:
        return self[1]

    def stage_item(self) -> Name:
        return self[3]

    def name(self) -> Name:
        return self[-1]

    def __str__(self) -> str:
        return f'@{".".join([str(e) for e in self])}'


SEARCH_CONFIG_PARENT = TypeVar("SEARCH_CONFIG_PARENT", bound=dict[str, any])


class SearchBy(Enum):
    XPATH = 'x-paths'
    SHADOW_ATTRIBUTE = 'shadow-attributes'


class SearchConfig:
    @staticmethod
    def of(config: SEARCH_CONFIG_PARENT, key: str) -> Union['SearchConfig', None]:
        """
         Example inputs:

         {'search-for': {'x-paths': '//*[@id="element-0"]'}}

         {'actions': ['wait 30']}  # No search config here

        :param config: The configuration dict from which to create a SearchConfig
        :param key: The key in the config dict. ['search-for'|'search-from']
        :return: The SearchConfig or None if there is no search config in the input
        """

        search_config = config.get(key)

        if search_config is None:
            return None
        elif isinstance(search_config, str):
            search_by = SearchBy.XPATH
            queries = [search_config]
        elif isinstance(search_config, list):
            search_by = SearchBy.XPATH
            queries = search_config
        elif isinstance(search_config, dict):
            search_by: SearchBy = [e for e in SearchBy if e.value in search_config.keys()][0]
            queries = search_config.get(search_by.value)
        else:
            raise ValueError(f'Invalid search config: {config}')

        return SearchConfig(search_by, queries)

    def __init__(self,
                 search_by: SearchBy,
                 queries: Union[str, list[str]]):
        self.__search_by = search_by
        self.__queries = [queries] if isinstance(queries, str) else queries
        self.__updated: bool = False

    def get_queries(self) -> [str]:
        return self.__queries

    def get_search_by(self) -> SearchBy:
        return self.__search_by

    def is_updated(self) -> bool:
        return self.__updated

    def reorder_queries(self, preferred_query_index: int) -> bool:
        if preferred_query_index < 1:
            return False
        result = [e for e in self.__queries]
        preferred_query: str = result.pop(preferred_query_index)
        logger.info(f"\n{'X=' * 32}\nPreferred query: {preferred_query}\n{'X=' * 32}")
        result.insert(0, preferred_query)
        self.__queries = result
        self.__updated = True
        return True


class SearchConfigs:
    @staticmethod
    def of(config: SEARCH_CONFIG_PARENT) -> 'SearchConfigs':
        return SearchConfigs(SearchConfig.of(config, 'search-for'),
                             SearchConfig.of(config, 'search-from'))

    def __init__(self, search_for: SearchConfig, search_from: Union[SearchConfig, None] = None):
        self.__search_from = search_from
        self.__search_for = search_for

    def search_from(self) -> Union[SearchConfig, None]:
        return self.__search_from

    def search_for(self) -> SearchConfig:
        return self.__search_for


STAGES_KEY: str = "stages"
STAGE_ITEMS_KEY: str = "stage-items"
WHEN_KEY: str = 'when'
ACTIONS_KEY: str = 'actions'
DEFAULT_ACTIONS_KEY: str = 'default-actions'
TIMEOUT_KEY: str = 'wait-timeout-seconds'
EVENTS = 'events'
ON_START = 'onstart'
ON_ERROR = 'onerror'
ON_SUCCESS = 'onsuccess'

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

    def events(self, config_path: ConfigPath, default: dict = None) -> dict[str, any]:
        return self.get(config_path, {}).get(EVENTS, default)

    def get_event_actions(self, config_path: ConfigPath, event_name: str) -> Union[str, list]:
        default_action: str = 'fail' if event_name == ON_ERROR else 'continue'
        str_or_list = self.events(config_path, {}).get(event_name, default_action)
        return self.__to_list(str_or_list)

    def is_continue_on_event(self, config_path: ConfigPath, event_name: str) -> bool:
        return self.get_event_actions(config_path, event_name) == 'continue'

    def get_actions(self, config_path: ConfigPath) -> list[str]:
        return self.get(config_path, {}).get(ACTIONS_KEY, [])

    def get_url(
            self, stage: Union[str, Name], result_if_none: Union[str, None]) -> Union[str, None]:
        return self.stage(stage, {}).get('url', result_if_none)

    def get_depends_on(self) -> [str]:
        return self.__config.get('depends-on', [])

    def get_wait_timeout(self,
                         path: Union[str, list[str], list[Name], tuple[Name]],
                         default: float = None) -> float:
        return self.get(path.join(TIMEOUT_KEY), default)

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

    def get_expectation_actions(self,
                                path: Union[str, list[str], list[Name], tuple[Name]]) -> list[str]:
        str_or_list = self.expected(path, {}).get(ACTIONS_KEY, [])
        return self.__to_list(str_or_list)

    @staticmethod
    def __to_list(source: Union[str, list]) -> list[str]:
        if isinstance(source, str):
            return [source]
        elif isinstance(source, list):
            return source
        else:
            raise ValueError(f'Invalid type for: {source}, expected list | str')

    def expected(self,
                 path: Union[str, list[str], list[Name], tuple[Name]],
                 default: dict[str, any] = None) -> dict[str, any]:
        return self.get(path, {}).get('expected', default)

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

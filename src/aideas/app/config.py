import copy
import logging
import os
import sys
from collections.abc import Iterable
from enum import Enum, unique
from typing import Union, TypeVar, Callable

from aideas.app.paths import Paths

logger = logging.getLogger(__name__)


def __default_get_keys(src: dict, tgt: dict) -> Iterable:
    return set(src.keys()).union(tgt.keys())


def update_config(src: dict[str, any],
                  tgt: dict[str, any],
                  keys: Iterable = None) -> dict[str, any]:
    if keys is None:
        keys = __default_get_keys(src, tgt)

    output = {}

    for key in keys:
        value = src.get(key)
        if value is None:
            value = tgt.get(key)
        if value is not None:
            output[key] = value
    return output


def merge_configs(src: dict[str, any],
                  tgt: dict[str, any],
                  merge_lists: bool = False,
                  get_keys: Callable[[dict, dict], Iterable] = __default_get_keys) \
        -> dict[str, any]:
    if not src:
        return copy.deepcopy(tgt)
    if not tgt:
        return copy.deepcopy(src)

    keys = get_keys(src, tgt)

    output = {}

    for key in keys:
        src_value = src.get(key)
        tgt_value = tgt.get(key)
        if src_value is None and tgt_value is None:
            continue
        ref_value = src_value if src_value is not None else tgt_value
        # We save our yaml comments
        # These config dicts come from yaml files.
        # This section of code will lead to loss of comments.
        # TODO - Implement preservation of comments
        if isinstance(ref_value, dict):
            output[key] = merge_configs(src_value, tgt_value, merge_lists, get_keys)
        elif merge_lists is True and isinstance(ref_value, list):
            existing_value = set() if not tgt_value else set(tgt_value)
            existing_value.update(src_value)
            output[key] = list(existing_value)
        else:
            output[key] = ref_value
    return output


class AppConfig:
    def __init__(self, config: dict[str, any]):
        self.__config = config.get('app', {})

    def get_title(self, default: Union[str, None] = None) -> str:
        return self.__config.get('title', default)


class BrowserConfig:
    def __init__(self, config: dict[str, any]):
        self.__config = config.get('browser', {})

    def get_executable_path(self, default: Union[str, None] = None) -> str:
        return self.chrome_config().get('executable_path', default)

    def is_undetected(self, default: Union[bool, None] = False) -> bool:
        return self.chrome_config().get('undetected', default)

    def get_options(self) -> list[str]:
        return self.chrome_config().get('options', {}).get('args', [])

    def get_download_dir(self, default: Union[str, None] = None) -> str:
        return self.prefs().get('download.default_directory', default)

    def prefs(self) -> dict[str, str]:
        return self.chrome_config().get('prefs', {})

    def chrome_config(self) -> dict[str, str]:
        return self.__config.get('chrome', {})


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

    def matches(self, text: str) -> bool:
        return self.__value == text or self.__id == text

    @property
    def id(self) -> str:
        return self.__id

    @property
    def value(self) -> str:
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

    def agent_str_path_simplified(self, agent: str, default: list[str] = None) -> list[str]:
        if self.is_stage_item() is False:
            return default
        path = [agent]
        path.extend(self.str_path_simplified())
        if len(path) < 3:
            return default
        if len(path) > 3:
            return path[0:3]
        return path

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

    def str_path_simplified(self) -> list[str]:
        path: list[str] = self.str_path()
        result: list[str] = []
        for e in path:
            if e == STAGES_KEY or e == STAGE_ITEMS_KEY:
                continue
            result.append(e)
        return result

    def str_path(self) -> list[str]:
        return [str(e) for e in self]

    def __str__(self) -> str:
        return f'@{".".join(self.str_path())}'


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

    def transform_queries(self, transform: Callable[[str], str]) -> 'SearchConfig':
        return SearchConfig(self.__search_by, [transform(query) for query in self.__queries])

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

    def __str__(self):
        return (f"SearchConfig{{search_by={self.__search_by}, queries={self.__queries}, "
                f"updated={self.__updated}}}")


class SearchConfigs:
    @staticmethod
    def of(config: SEARCH_CONFIG_PARENT) -> 'SearchConfigs':
        return SearchConfigs(SearchConfig.of(config, 'search-for'),
                             SearchConfig.of(config, 'search-from'))

    def __init__(self, search_for: SearchConfig, search_from: Union[SearchConfig, None] = None):
        self.__search_from = search_from
        self.__search_for = search_for

    def transform_queries(self, transform: Callable[[str], str]) -> 'SearchConfigs':
        search_for = self.search_for()
        search_from = self.search_from()
        return SearchConfigs(
            None if search_for is None else search_for.transform_queries(transform),
            None if search_from is None else search_from.transform_queries(transform))

    def search_from(self) -> Union[SearchConfig, None]:
        return self.__search_from

    def search_for(self) -> SearchConfig:
        return self.__search_for


STAGES_KEY: str = "stages"
STAGE_ITEMS_KEY: str = "stage-items"
WHEN_KEY: str = 'when'
ACTIONS_KEY: str = 'actions'
DEFAULT_ACTIONS_KEY: str = 'default-actions'
TIMEOUT_KEY: str = 'timeout-seconds'
EVENTS = 'events'
ON_START = 'onstart'
ON_ERROR = 'onerror'
ON_SUCCESS = 'onsuccess'

VALUE = TypeVar("VALUE", bound=Union[any, None])


def check_for_typo(config: dict[str, any], valid_key: str) -> dict[str, any]:
    """
    Check if the config contains any key with a typo in its spelling.
    :param config: The dict to check
    :param valid_key: The valid key for which misspelled variants are to be checked
    :return: None
    """
    last_char_missing: str = valid_key[:-1]
    if config.get(last_char_missing):
        raise ValueError(f'Invalid key: "{last_char_missing}", use "{valid_key}" instead.')
    return config


class AgentConfig:
    @staticmethod
    def is_default_actions_key(stage_item: Union[str, Name]) -> bool:
        return AgentConfig.__value(stage_item) == DEFAULT_ACTIONS_KEY

    def __init__(self, config: dict[str, any]):
        self.__config = check_for_typo(config, STAGES_KEY)

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
        stage: dict = self.stage(self.__value(stage), {})
        check_for_typo(stage, STAGE_ITEMS_KEY)
        return stage.get(STAGE_ITEMS_KEY, result_if_none)

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

    def get_iteration_index_variable(self, config_path: ConfigPath, default: str = 'index') -> str:
        iteration: dict = self.iteration(config_path, {})
        result = iteration.get('index_variable', default)
        # The . character is used to separate path elements in the config
        # $context.<stage>.<stage-item> Has a meaning made possible by the . character
        if '.' in result:
            raise ValueError(f'Invalid character `.` in index variable: {result}')
        return result

    @staticmethod
    def get_default_iteration_index_variable(config_path: ConfigPath) -> str:
        index_path = config_path.str_path_simplified()
        index_path.extend(['iteration', 'index'])
        return ".".join(index_path)

    def get_iteration_start(self, config_path: ConfigPath, default: int = 0) -> int:
        iteration: dict = self.iteration(config_path, {})
        return iteration.get('start', default)

    def get_iteration_step(self, config_path: ConfigPath, default: int = 1) -> int:
        iteration: dict = self.iteration(config_path, {})
        return iteration.get('step', default)

    def get_iteration_end(self, config_path: ConfigPath, default: int = 1) -> int:
        iteration: dict = self.iteration(config_path, {})
        return iteration.get('end', default)

    def iteration(self, config_path: ConfigPath, default: dict = None) -> dict[str, any]:
        return self.get(config_path, {}).get("iteration", default)

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

    def is_clear_output_dir(self) -> bool:
        return self.__config.get('clear-output-dir', True)

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
        return None if name is None else Name.of(name).value


def tokenize(value: str, separator: str = ' ') -> list[str]:
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


def parse_query(value: str, separator=' ') -> dict[str, str]:
    """
    Converts a string to a dictionary of attributes.
    Input: key_0=value_0 key_1="value with spaces"
    Output: {key_0: value_0, key_1: value with spaces}
    :param value: The value to parse into a dictionary.
    :param separator: The separator between the attribute pairs.
    :return: The dictionary of attributes.
    """
    value = value.replace('=', separator)
    result: list[str] = tokenize(value, separator)
    return __list_to_dict(result)


"""
The following code is used to parse command line arguments.
"""
T = TypeVar("T", bound=any)


@unique
class RunArg(str, Enum):
    def __new__(cls, value, alias: str = None, kind: str = 'str',
                optional: bool = False, path: bool = False):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__alias = alias
        obj.__type = kind
        obj.__optional = optional
        obj.__path = path
        return obj

    @property
    def alias(self) -> str:
        return self.__alias

    @property
    def type(self) -> str:
        return self.__type

    @property
    def is_optional(self) -> bool:
        return self.__optional

    @property
    def is_path(self) -> bool:
        return self.__path

    AGENTS = ('agents', 'a', 'list')
    VIDEO_CONTENT_FILE = ('video-content-file', 'vcf', 'str', False, True)
    VIDEO_TITLE = ('video-title', 'vt', 'str', True, False)
    VIDEO_DESCRIPTION = ('video-description', 'vd', 'str', True, False)
    VIDEO_INPUT_FILE = ('video-input-file', 'vif', 'str', True, True)
    VIDEO_INPUT_TEXT = ('video-input-text', 'vit', 'str', True, False)
    VIDEO_COVER_IMAGE = ('video-cover-image', 'vci', 'str', False, True)
    VIDEO_COVER_IMAGE_SQUARE = ('video-cover-image-square', 'vcis', 'str', True, True)

    @staticmethod
    def values() -> [str]:
        return [RunArg(e).value for e in RunArg]

    @staticmethod
    def collect(add_to: dict[str, any] = None) -> dict[str, any]:
        if add_to is None:
            add_to = {}
        for e in RunArg:
            arg = RunArg(e)
            if arg.type == "list":
                value = RunArg.get_list_arg_value(arg)
            else:
                value = RunArg.get_arg_value(arg)
            if not value:
                continue
            if arg.is_path:
                value = Paths.get_path(value) if arg.is_optional else Paths.require_path(value)
            add_to[arg] = value

        return add_to

    @staticmethod
    def get_list_arg_value(arg_name: 'RunArg') -> [str]:
        return RunArg.__get_formatted_arg(arg_name, lambda x: x.split(','), [])

    @staticmethod
    def __get_formatted_arg(arg: 'RunArg',
                            convert: Callable[[str], T],
                            result_if_none: Union[T, None] = None) -> T:
        arg_value = RunArg.get_arg_value(arg, None)
        return result_if_none if arg_value is None else convert(arg_value)

    @staticmethod
    def get_arg_value(arg: 'RunArg', result_if_none: Union[any, None] = None) -> any:
        """
        Get the value of the argument with the given name.
        Arguments have aliases that can be used to refer to them.
        --agents twitter could be written as -a twitter
        :param arg: The argument.
        :param result_if_none: The result to return if none
        :return: The value of the argument with the given name.
        """
        sys_args: [str] = [e.lower() for e in sys.argv]
        candidates: [str] = [f'--{arg.value}', f'-{arg.alias}']
        for candidate in candidates:
            if candidate in sys_args:
                return sys_args[sys_args.index(candidate) + 1]
        return result_if_none if not arg.value else os.environ.get(arg.name, result_if_none)

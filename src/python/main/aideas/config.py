import logging
from enum import Enum
from typing import Union, TypeVar

logger = logging.getLogger(__name__)


class Name:
    @staticmethod
    def of_list(names: list[str], alias: Union[str, None] = None) -> ['Name']:
        aliases = [names] if alias is None else [alias for _ in names]
        return Name.of_lists(names, aliases)

    @staticmethod
    def of_lists(names: list[str], aliases: Union[list[str], None] = None) -> ['Name']:
        if aliases is not None and len(names) != len(aliases):
            raise ValueError("The number of names and aliases must be the same")
        if aliases is None:
            aliases: [str] = [name for name in names]
        return [Name(names[i], aliases[i]) for i in range(len(names))]

    @staticmethod
    def of(name: str, alias: Union[str, None] = None) -> 'Name':
        return Name(name, alias)

    def __init__(self, name: str, alias: Union[str, None] = None):
        if name is None:
            raise ValueError('name cannot be None')
        self.value = name
        self.id = name if alias is None else alias

    def __eq__(self, other) -> bool:
        return self.value == other.value and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.value) + hash(self.id)

    def __str__(self) -> str:
        return self.value if self.value == self.id else f'({self.value}|{self.id})'


SEARCH_CONFIG_PARENT = TypeVar("SEARCH_CONFIG_PARENT", bound=Union[str, dict])


class SearchBy(Enum):
    XPATH = 'search-x-paths'
    SHADOW_ATTRIBUTE = 'search-shadow-attributes'


class SearchConfig:
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
    #
    # @staticmethod
    # def update(
    #         config: SEARCH_CONFIG_PARENT, elem_search_cfg: 'SearchConfig') -> SEARCH_CONFIG_PARENT:
    #     if elem_search_cfg.__successful_query_index < 1:
    #         return config
    #
    #     if isinstance(config, str):
    #         return config
    #     elif isinstance(config, dict):
    #         search_config = SearchConfig.__get_search_config(config)
    #         search_by = SearchConfig.__get_search_by(config)
    #
    #         if search_config is None:
    #             return config
    #         elif isinstance(search_config, str):
    #             return config
    #         elif isinstance(search_config, list):
    #             logger.debug(f"Before: {config}")
    #             config[search_by] = elem_search_cfg.reorder_search_for()
    #             logger.debug(f" After: {config}")
    #             return config
    #         elif isinstance(search_config, dict):
    #             logger.debug(f"Before: {config}")
    #             config[search_by]['search-for'] = elem_search_cfg.reorder_search_for()
    #             logger.debug(f" After: {config}")
    #             return config
    #         else:
    #             raise ValueError(f'Invalid search config: {config}')
    #     else:
    #         raise ValueError(f'Invalid search config: {config}')

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

VALUE = TypeVar("VALUE", bound=Union[any, None])


class AgentConfig:
    @staticmethod
    def is_default_actions_key(stage_item: Union[str, Name]) -> bool:
        return AgentConfig.__value(stage_item) == DEFAULT_ACTIONS_KEY

    @staticmethod
    def path(stage: Union[str, Name], stage_item: Union[str, Name] = None) -> [str]:
        path = [STAGES_KEY, AgentConfig.__value(stage)]
        if not stage_item:
            return path
        path.append(STAGE_ITEMS_KEY)
        path.append(AgentConfig.__value(stage_item))
        return path

    def __init__(self, config: dict[str, any]):
        self.__config = config

    def root(self) -> dict[str, any]:
        return self.__config

    def stages(self,
               path: Union[str, list[str], list[Name], None] = None,
               result_if_none=None) -> Union[dict[str, any], any, None]:
        if not path:
            return self.__config[STAGES_KEY]
        else:
            path = [e for e in path]
            path.insert(0, STAGES_KEY)
            return self.get(path, result_if_none)

    def get_stage_names(self) -> [Name]:
        return Name.of_lists(list(self.stages().keys()))

    def stage(self, stage: Union[str, Name], result_if_none = None) -> any:
        return self.stages().get(self.__value(stage), result_if_none)

    def stage_items(self, stage: Union[str, Name], result_if_none = None) -> any:
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

    def search(self, stage: Union[str, Name], stage_item: Union[str, Name]) -> dict[str, any] or None:
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
        return self.get_stage_value(stage, 'wait-timeout-seconds', result_if_none)

    def get_stage_value(self, stage: Union[str, Name], key: str, result_if_none: VALUE = 0) -> VALUE:
        return self.stage(stage, {}).get(key, result_if_none)

    def get_stage_item_wait_timeout(
            self, stage: Union[str, Name], item: Union[str, Name], result_if_none: int = 0) -> int:
        return self.get_stage_item_value(stage, item, 'wait-timeout-seconds', result_if_none)

    def get_stage_item_value(self,
                             stage: Union[str, Name],
                             item: Union[str, Name],
                             key: str,
                             result_if_none: VALUE = 0) -> VALUE:
        return self.stage_item(stage, item, {}).get(key, result_if_none)

    def get(self, path: Union[str, list[str], list[Name]], result_if_none=None) -> any:
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
    def __value_list(path: Union[str, list[str], list[Name]]) -> [str]:
        if isinstance(path, str):
            return [path]
        result = []
        for e in path:
            result.append(e if isinstance(e, str) else AgentConfig.__value(e))
        return result

    @staticmethod
    def __value(name: Union[str, Name]) -> Union[str, None]:
        if name is None:
            return None
        return name if isinstance(name, str) else name.value
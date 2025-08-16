from collections.abc import Iterable
from typing import Callable, Union

import logging
import os

from pyu.io.file import load_yaml
from pyu.io.yaml_loader import YamlLoader
from .action.variable_parser import replace_all_variables, get_variables
from .config import RunArg, merge_configs, AgentConfig
from .env import Env, is_production
from .paths import Paths

logger = logging.getLogger(__name__)

_SUFFIX = '.config'


class ConfigLoader(YamlLoader):
    def __init__(self,
                 config_path: str,
                 variable_source: Union[dict[str, any], None] = None):
        super().__init__(config_path, suffix=_SUFFIX)
        self.__config_path = config_path
        self.__variable_source = variable_source if variable_source else Env.collect()
        self.__external_config_dir = Paths.get_path(self.__variable_source.get(Env.CONFIG_DIR.value))
        # Only load this when we are about to run an agent.
        # self.__variable_source.update(self.load_run_config()) # run properties
        self.__variable_source.update(RunArg.of_defaults()) # sys.argv and environment variable RUN_ARGs
        self.__agent_configs_with_un_replaced_variables = self.__load_agent_config_with_variables()

    def with_added_variable_source(self, source: dict[str, any]) -> 'ConfigLoader':
        return ConfigLoader(self.__config_path, {**self.__variable_source, **source})

    def get_agent_variable_names(self, agent_name: str) -> list[str]:
        config = self.__agent_configs_with_un_replaced_variables[agent_name]
        return get_variables(config, False)

    def get_agent_names(self, tag: Union[str , None] = None) -> list[str]:
        def config_filter(config: dict[str, any]) -> bool:
            agent_tags = AgentConfig(config).get_agent_tags()
            if is_production() is True and 'test' in agent_tags:
                return False
            return not tag or tag in agent_tags

        def config_sort(config: dict[str, any]) -> int:
            return AgentConfig(config).get_sort_order()

        return self.get_sorted_agent_names(config_filter, config_sort)

    def get_sorted_agent_names(self,
                               config_filter: Callable[[dict[str, any]], bool],
                               config_sort: Callable[[dict[str, any]], int]) -> list[str]:
        keys = []
        values = []
        for k, v in self.__agent_configs_with_un_replaced_variables.items():
            if config_filter(v):
                keys.append(k)
                values.append(v)
        values_sorted = list(values)
        values_sorted.sort(key=config_sort)

        return [keys[values.index(sorted_val)] for sorted_val in values_sorted]

    def load_run_config(self, check_replaced: bool = True) -> dict[str, any]:
        result = self.load_from_path(self.get_path("run"), check_replaced)
        result = RunArg.of_dict(result)
        result.update(RunArg.of_defaults())
        return result

    def load_browser_config(self, check_replaced: bool = True) -> dict[str, any]:
        browser_type = self.load_run_config().get(RunArg.BROWSER_TYPE.value, None)
        return self._load_browser_config_for_type(browser_type, check_replaced)

    def add_browser_config_to_agent_config(self, agent_config: dict[str, any], check_replaced: bool = True) -> dict[str, any]:
        browser_type = self.load_run_config().get(RunArg.BROWSER_TYPE.value, None)
        if browser_type is None:
            browser_type = agent_config.get(RunArg.BROWSER_TYPE.value, None)
        browser_config = self._load_browser_config_for_type(browser_type, check_replaced)
        if browser_type is not None and agent_config.get('browser', None) is not None:
            logger.warning(f"browser-{browser_type}.config will be overridden by agent browser config")
        agent_config['browser'] = merge_configs(
            agent_config.get('browser', {}), browser_config, False)
        return agent_config

    def load_agent_config(self, agent_name: str, check_replaced: bool = True) -> dict[str, any]:
        return self.load_from_path(self.get_agent_config_path(agent_name), check_replaced)

    def load_from_path(self, path: str, check_replaced: bool = True) -> dict[str, any]:
        return self.__load_from_path(path, self.__variable_source, check_replaced)

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.get_path(os.path.join('agent', agent_name))

    def get_all_agent_names(self) -> list[str]:
        agents = []
        agent_dir = os.path.join(os.path.dirname(self.get_path("app")), 'agent')
        for agent_filename in os.listdir(agent_dir):
            agents.append(agent_filename[0:agent_filename.index(_SUFFIX)])
        return agents

    def _load_browser_config_for_type(self, browser_type: str, check_replaced: bool = True) -> dict[str, any]:
        if browser_type == 'visible':
            config_name = 'browser-visible'
        elif browser_type == 'undetected':
            config_name = 'browser-undetected'
        else:
            config_name = 'browser'
        return self.load_from_path(self.get_path(config_name), check_replaced)

    def __load_agent_config_with_variables(self) -> dict[str, dict[str, any]]:
        configs = {}
        for name in self.get_all_agent_names():
            configs[name] = self.__load_from_path(self.get_agent_config_path(name), {}, False)
        logger.debug(f"Config names: {configs.keys()}")
        return configs

    def __load_from_path(self,
                         path: str,
                         variables: Union[dict[str, any], None] = None,
                         check_replaced: bool = True) -> dict[str, any]:
        loaded: dict[str, any] = self.__load_from_path_with_variables_replaced(
            path, variables, check_replaced)
        if self.__external_config_dir:
            external_path = os.path.join(self.__external_config_dir, os.path.split(path)[1])
            external_config = self.__load_from_path_with_variables_replaced(
                external_path, variables, check_replaced, False)
            if external_config:
                loaded.update(external_config)
        return loaded

    def __load_from_path_with_variables_replaced(
            self,
            path: str,
            variables: Union[dict[str, any], None] = None,
            check_replaced: bool = True, log: bool = True) -> dict[str, any]:
        try:
            return replace_all_variables(self.__load_from_yaml(path), variables, check_replaced)
        except FileNotFoundError:
            if log:
                print(f'Could not find config file for: {path}')
            return {}

    def __load_from_yaml(self, path: str) -> dict[str, any]:
        loaded = load_yaml(path)
        parent_name = loaded.pop("extends", "")
        if parent_name:
            parent_path = f"{os.path.join(os.path.dirname(path), parent_name)}{_SUFFIX}.yaml"
            parent = self.__load_from_yaml(parent_path)
            if parent:
                loaded = merge_configs(loaded, parent, False, ConfigLoader.__get_keys_for_merging)
        return loaded

    @staticmethod
    def __get_keys_for_merging(candidate: dict, parent: dict) -> Iterable:
        parent_keys = list(parent.keys())
        candidate_keys = list(candidate.keys())
        parent_keys.extend(x for x in candidate_keys if x not in parent_keys)
        return parent_keys

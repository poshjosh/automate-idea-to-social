from collections.abc import Iterable

import logging
import os
from typing import Callable

from pyu.io.file import load_yaml
from pyu.io.yaml_loader import YamlLoader
from .action.variable_parser import replace_all_variables, get_variables
from .config import RunArg, merge_configs
from .env import Env
from .paths import Paths

logger = logging.getLogger(__name__)

_SUFFIX = '.config'


class ConfigLoader(YamlLoader):
    def __init__(self,
                 config_path: str,
                 variable_source: dict[str, any] or None = None):
        super().__init__(config_path, suffix=_SUFFIX)
        self.__config_path = config_path
        self.__variable_source = variable_source if variable_source else Env.collect()
        self._add_variable_source(RunArg.of_sys_argv()) # sys.argv
        self.__external_config_dir = Paths.get_path(self.__variable_source.get(Env.CONFIG_DIR.value))
        print(f'External config dir: {self.__external_config_dir}')
        self.__agent_configs_with_un_replaced_variables = self.load_agent_configs(False)

    def with_added_variable_source(self, source: dict[str, any]) -> 'ConfigLoader':
        return ConfigLoader(self.__config_path, self.__variable_source)._add_variable_source(source)

    def get_agent_variable_names(self, agent_name: str) -> [str]:
        config = self.__agent_configs_with_un_replaced_variables[agent_name]
        return get_variables(config, False)

    def get_sorted_agent_names(self,
                               config_filter: Callable[[dict[str, any]], bool],
                               config_sort: Callable[[dict[str, any]], int]) -> [str]:
        keys = []
        values = []
        for k, v in self.__agent_configs_with_un_replaced_variables.items():
            if config_filter(v):
                keys.append(k)
                values.append(v)
        values_sorted = [e for e in values]
        values_sorted.sort(key=config_sort)

        return [keys[values.index(sorted_val)] for sorted_val in values_sorted]

    def load_run_config(self) -> dict[str, any]:
        result = self.load_config("run")
        return RunArg.of_dict(result)

    def load_browser_config(self) -> dict[str, any]:
        browser_visible = self.__variable_source.get(RunArg.BROWSER_VISIBLE.value, False)
        logger.debug(f"Browser visible: {browser_visible}")
        return self.load_config("browser-visible" if browser_visible else "browser")

    def load_agent_configs(
            self, check_replaced: bool = True, cfg_filter=None) -> dict[str, dict[str, any]]:
        configs = {}
        for name in self.get_all_agent_names():
            config = self.load_agent_config(name, check_replaced)
            if not cfg_filter or cfg_filter(config):
                configs[name] = config
        logger.debug(f"Config names: {configs.keys()}")
        return configs

    def load_agent_config(self, agent_name: str, check_replaced: bool = True) -> dict[str, any]:
        return self.load_from_path(self.get_agent_config_path(agent_name), check_replaced)

    def load_from_path(self, path: str, check_replaced: bool = True) -> dict[str, any]:
        loaded: dict[str, any] = self._load_from_path(path, check_replaced)
        if self.__external_config_dir:
            external_path = os.path.join(self.__external_config_dir, os.path.split(path)[1])
            external_config = self._load_from_path(external_path, check_replaced, False)
            if external_config:
                loaded.update(external_config)
        return loaded

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.get_path(os.path.join('agent', agent_name))

    def get_all_agent_names(self) -> [str]:
        agents = []
        agent_dir = os.path.join(os.path.dirname(self.get_path("app")), 'agent')
        for agent_filename in os.listdir(agent_dir):
            agents.append(agent_filename[0:agent_filename.index(_SUFFIX)])
        return agents

    def get_variable_source(self) -> dict[str, any]:
        return {**self.__variable_source}

    def _add_variable_source(self, source: dict[str, any]) -> 'ConfigLoader':
        self.__variable_source.update(source)
        return self

    def _load_from_path(self, path: str, check_replaced: bool = True, log: bool = True) -> dict[str, any]:
        try:
            return replace_all_variables(
                self.__load_from_yaml(path), self.__variable_source, check_replaced)
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

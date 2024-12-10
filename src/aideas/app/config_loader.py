import logging
import os
from typing import Callable

from pyu.io.file import load_yaml
from pyu.io.yaml_loader import YamlLoader
from .action.variable_parser import replace_all_variables
from .config import RunArg
from .env import Env

logger = logging.getLogger(__name__)


_SUFFIX = '.config'


class ConfigLoader(YamlLoader):
    def __init__(self, config_path: str, run_config: dict[str, any] = None):
        super().__init__(config_path, suffix=_SUFFIX)
        self.__variable_source = {}
        self.__variable_source.update(Env.collect())  # Environment variables
        if run_config is None:
            self.__variable_source.update(self.load_run_config())  # Properties file
        self.__variable_source.update(RunArg.of_sys_argv())  # sys.argv
        if run_config is not None:
            self.__variable_source.update(run_config)  # User supplied
        self.__agent_configs = self.load_agent_configs()

    def get_sorted_agent_names(self,
                               config_filter: Callable[[dict[str, any]], bool],
                               config_sort: Callable[[dict[str, any]], int]) -> [str]:
        keys = []
        values = []
        for k, v in self.__agent_configs.items():
            if config_filter(v):
                keys.append(k)
                values.append(v)
        values_sorted = [e for e in values]
        values_sorted.sort(key=config_sort)

        return [keys[values.index(sorted_val)] for sorted_val in values_sorted]

    def load_agent_configs(self, cfg_filter=None) -> dict[str, dict[str, any]]:
        configs = {}
        for name in self.__all_agent_names():
            config = self.load_agent_config(name)
            if not cfg_filter or cfg_filter(config):
                configs[name] = config
        logger.debug(f"Config names: {configs.keys()}")
        return configs

    def __all_agent_names(self) -> [str]:
        agents = []
        agent_dir = os.path.join(os.path.dirname(self.get_path("app")), 'agent')
        for agent_filename in os.listdir(agent_dir):
            agents.append(agent_filename[0:agent_filename.index(_SUFFIX)])
        return agents

    def load_run_config(self) -> dict[str, any]:
        result = self.load_config("run")
        return RunArg.of_dict(result)

    def load_from_path(self, path: str) -> dict[str, any]:
        try:
            return replace_all_variables(load_yaml(path), self.__variable_source)
        except FileNotFoundError:
            logger.warning(f'Could not find config file for: {path}')
            return {}

    def load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.load_from_path(self.get_agent_config_path(agent_name))

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.get_path(os.path.join('agent', agent_name))

import logging
import os

from .action.variable_parser import replace_all_variables

from pyu.io.file import load_yaml
from pyu.io.yaml_loader import YamlLoader

logger = logging.getLogger(__name__)


class ConfigLoader(YamlLoader):
    def __init__(self, config_path: str):
        super().__init__(config_path, transform=replace_all_variables, suffix='.config')
        self.__config_path = config_path

    def load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.__load_from_path(self.get_agent_config_path(agent_name))

    def __load_from_path(self, path: str) -> dict[str, any]:
        try:
            return replace_all_variables(load_yaml(path))
        except FileNotFoundError:
            logger.warning(f'Could not find config file for: {path}')
            return {}

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.__get_path(os.path.join('agent', agent_name))

    def __get_path(self, id_str: str) -> str:
        return os.path.join(self.__config_path, f'{id_str}.config.yaml')

import logging
import os

from .io.file import load_yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    @staticmethod
    def load_from_path(yaml_file_path) -> dict[str, any]:
        return load_yaml(yaml_file_path)

    def __init__(self, config_path: str):
        self.__config_path = config_path

    def load_app_config(self) -> dict[str, any]:
        return self.__load_from_path(self.get_app_config_path())

    def load_logging_config(self) -> dict[str, any]:
        return self.__load_from_path(self.get_logging_config_path())

    def load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.__load_from_path(self.get_agent_config_path(agent_name))

    def __load_from_path(self, path: str) -> dict[str, any]:
        try:
            return self.load_from_path(path)
        except FileNotFoundError:
            logger.warning(f'Could not find config file for: {path}')
            return {}

    def get_app_config_path(self) -> str:
        return self.__get_path('app')

    def get_logging_config_path(self) -> str:
        return self.__get_path('logging')

    def get_agent_config_path(self, agent_name: str) -> str:
        return self.__get_path(os.path.join('agent', agent_name))

    def __get_path(self, id_str: str) -> str:
        return os.path.join(self.__config_path, f'{id_str}.config.yaml')

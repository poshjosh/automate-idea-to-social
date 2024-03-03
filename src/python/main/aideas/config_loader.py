import logging
import os
import yaml

from .env import Env

logger = logging.getLogger(__name__)


class ConfigLoader:
    @staticmethod
    def load_from_path(yaml_file_path) -> dict[str, any]:
        with open(yaml_file_path, 'r') as config_file:
            logger.info(f'Will load config from: {yaml_file_path}')
            config = yaml.safe_load(config_file.read())
            logger.info(f'Loaded config: {config}')
            # Environment vars will override any existing vars
            env = Env.collect()
            for key, value in env.items():
                config[key] = value
            return config

    def __init__(self, config_path: str):
        self.__config_path = config_path

    def load_app_config(self) -> dict[str, any]:
        return self.load_from_id('app')

    def load_logging_config(self) -> dict[str, any]:
        return self.load_from_id('logging')

    def load_agent_config(self, agent_name: str) -> dict[str, any]:
        return self.load_from_id(os.path.join('agent', agent_name))

    def load_from_id(self, id_str: str) -> dict[str, any]:
        try:
            return self.load_from_path(self.get_path_from_id(id_str))
        except FileNotFoundError:
            logger.warning(f'Could not find config file for: {id_str}')
            return {}

    def get_path_from_id(self, id_str: str) -> str:
        return self.get_path(f'{id_str}.config.yaml')

    def get_path(self, path: str) -> str:
        return os.path.join(self.__config_path, path)

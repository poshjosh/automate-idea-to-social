import logging
import os
import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    @staticmethod
    def load_from_id(name: str) -> dict[str, any]:
        try:
            return ConfigLoader.load_from_path(
                f'{ConfigLoader.get_config_path()}/{name}.config.yaml')
        except FileNotFoundError:
            logger.warning(f'Could not find config file for agent: {name}')
            return {}

    @staticmethod
    def get_config_path() -> str:
        return 'aideas/config'

    @staticmethod
    def load_from_path(yaml_file_path) -> dict[str, any]:
        with open(yaml_file_path, 'r') as config_file:
            logger.info(f'Will load app config from: {yaml_file_path}')
            config = yaml.safe_load(config_file.read())
            logger.info(f'Loaded app config: {config}')
            # Environment vars will override any existing vars
            env = dict(os.environ)
            for key, value in env.items():
                config[key] = value
            return config

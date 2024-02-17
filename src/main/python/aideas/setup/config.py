import logging.config
import os
import yaml


logger = logging.getLogger(__name__)


class AppConfig:
    def load(self, yaml_file_path: str = 'aideas/setup/config.yaml') -> dict:
        with open(yaml_file_path, 'r') as config_file:
            logger.info(f'Will load app config from: {yaml_file_path}')
            config = yaml.safe_load(config_file.read())
            logger.info(f'Loaded app config: {config}')
            # Environment vars will override any existing vars
            env = dict(os.environ)
            for key, value in env.items():
                config[key] = value
            return config

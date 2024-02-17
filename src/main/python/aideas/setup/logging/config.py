import logging.config
import yaml


logger = logging.getLogger(__name__)


class LoggingConfig:
    def load(self, yaml_file_path='aideas/setup/logging/config.yaml'):
        with open(yaml_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file.read())
            logging.config.dictConfig(config)
            logger.info(f'Done loading logging configuration from: {config_file}')

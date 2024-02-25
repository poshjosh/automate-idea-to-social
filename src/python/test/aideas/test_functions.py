import os
from typing import Union

from selenium import webdriver

from ...main.aideas.config_loader import ConfigLoader
from ...main.aideas.web.webdriver_creator import WebDriverCreator

MAIN_SRC_DIR = f'{os.getcwd()}/python/main/aideas'
TEST_SRC_DIR = f'{os.getcwd()}/python/test/aideas'


def get_logging_config() -> dict[str, any]:
    return {
        'version':1,
        'formatters':{'simple':{'format':'%(asctime)s %(name)s %(levelname)s %(message)s'}},
        'handlers': {'console':{'class':'logging.StreamHandler', 'level':'DEBUG', 'formatter':'simple'}},
        'loggers':{'python':{'level': 'DEBUG', 'handlers':['console'], 'propagate':'no'}}
    }


def load_app_config() -> dict[str, any]:
    config_file = f'{MAIN_SRC_DIR}/config/app.config.yaml'
    print(f'config_file: {config_file}')
    config: dict[str, any] = ConfigLoader.load_from_path(config_file)
    print(f'config: {config}')
    return config


def load_agent_config(agent: str):

    config_file = f'{MAIN_SRC_DIR}/config/agent/{agent}.config.yaml'
    print(f'config_file: {config_file}')
    config: dict[str, any] = ConfigLoader.load_from_path(config_file)
    print(f'config: {config}')
    return config


def create_webdriver(config: Union[dict, None] = None) -> webdriver:
    if config is None:
        config = load_app_config()
    return WebDriverCreator.create(config)


def get_agent_resource(agent_name: str, file_name: str) -> str:
    return f'file:///{TEST_SRC_DIR}/agent/{agent_name}/resources/{file_name}'

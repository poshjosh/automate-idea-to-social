import os
from typing import Union, Callable

from selenium import webdriver

from ....main.app.aideas.action.action_result import ActionResult
from ....main.app.aideas.config_loader import ConfigLoader
from ....main.app.aideas.result.result_set import ElementResultSet
from ....main.app.aideas.web.webdriver_creator import WebDriverCreator

__MAIN_SRC_DIR = f'{os.getcwd()}/python/main/app/aideas'
__TEST_SRC_DIR = f'{os.getcwd()}/python/test/app/aideas'


def get_main_path(file_path: str) -> str:
    return os.path.join('python', 'main', file_path)


def get_test_path(file_path: str) -> str:
    return os.path.join('python', 'test', file_path)


def get_config_loader() -> ConfigLoader:
    return ConfigLoader(get_main_path('resources/config'))


def init_logging(config):
    config.dictConfig(__get_logging_config())


def __get_logging_config() -> dict[str, any]:
    return {
        'version': 1,
        'formatters': {'simple': {'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}},
        'handlers': {'console': {'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'simple'}},
        'loggers': {'python': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False}}
    }


def create_webdriver(config: Union[dict, None] = None, agent_name: str = None) -> webdriver:
    if config is None:
        config = get_config_loader().load_app_config()

    chrome_config = config.get("browser", {}).get("chrome", {})

    args = chrome_config.get("options", {}).get("args", [])

    for e in args:
        if e.startswith("window-size="):
            args.remove(e)
            break

    if "start-maximized" in args:
        args.remove("start-maximized")
    if "kiosk" in args:
        args.remove("kiosk")
    if "headless" not in args:
        args.append("headless")

    # For now undetected Chrome browser is crashing during tests.
    # So we set undetected to False, for the time being.
    chrome_config['undetected'] = False

    return WebDriverCreator.create(config)


def get_agent_resource(agent_name: str, file_name: str) -> str:
    test_path = get_test_src_path(f'agent/{agent_name}/resources/{file_name}')
    return f'file:///{test_path}'


def get_main_src_path(file_path: str) -> str:
    return os.path.join(__MAIN_SRC_DIR, file_path)


def get_test_src_path(file_path: str) -> str:
    return os.path.join(__TEST_SRC_DIR, file_path)


def delete_saved_files(result_set: ElementResultSet, test: Callable[[str], bool] = None):
    for element_name in result_set.keys():
        result_list: list[ActionResult] = result_set.get(element_name)
        __delete_file_results(result_list, test)


def __delete_file_results(result_list: list[ActionResult], test: Callable[[str], bool] = None):
    for r in result_list:
        file = r.get_result()
        if file is None or os.path.sep not in file or '/' not in file:
            continue
        may_proceed = True if test is None else test(file)
        if not may_proceed:
            continue
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f'{__name__} Successfully removed file: {file}')
        except Exception as ex:
            print(f'{__name__} Failed to remove file: {file}. {str(ex)}')
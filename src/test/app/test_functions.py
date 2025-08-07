import os
from typing import Union, Callable

from selenium import webdriver

from aideas.app.action.action_result import ActionResult
from aideas.app.config import RunArg
from aideas.app.config_loader import ConfigLoader, SimpleConfigLoader
from aideas.app.result.result_set import ElementResultSet
from aideas.app.run_context import RunContext
from aideas.app.web.webdriver_creator import WebDriverCreator

__TEST_SRC_DIR = f'{os.getcwd()}/test/app'


class TestConfigLoader(SimpleConfigLoader):
    def __init__(self, config_path: str, variable_source: dict[str, any] or None = None):
        super().__init__(config_path, variable_source)

    def _init_variable_source(self):
        super()._add_variable_source(self.load_run_config())  # Properties file
        super()._init_variable_source()


def get_main_config_loader(variable_source: dict[str, any] or None = None) -> ConfigLoader:
    return TestConfigLoader(os.path.join("resources", "config"), variable_source)


def get_test_config_loader(variable_source: dict[str, any] or None = None) -> ConfigLoader:
    return TestConfigLoader(os.path.join("test", "resources", "config"), variable_source)


def load_agent_names() -> [str]:
    return get_main_config_loader().load_agent_configs().keys()


def load_app_config() -> dict[str, any]:
    return get_main_config_loader().load_app_config()


def load_agent_config(agent_name: str, check_replaced: bool = True) -> dict[str, any]:
    return get_main_config_loader().load_agent_config(agent_name, check_replaced)


def load_run_config(agent_names: [str] = None) -> dict[str, any]:
    run_config = get_test_config_loader().load_run_config()
    if agent_names:
        run_config[RunArg.AGENTS] = agent_names
    return run_config


def get_run_context(agent_names: [str] = None) -> RunContext:
    return RunContext.of_config(load_app_config(), load_run_config(agent_names))


def init_logging(config):
    config.dictConfig(__get_logging_config())


def __get_logging_config() -> dict[str, any]:
    return {
        'version': 1,
        'formatters': {'simple': {'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}},
        'handlers': {'console': {
            'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'simple'}},
        'loggers': {'test': {'level': 'DEBUG', 'handlers': ['console'], 'propagate': False}}
    }


def create_webdriver(config: Union[dict, None] = None, agent_name: str = None) -> webdriver:
    if config is None:
        config = get_main_config_loader().load_app_config()

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
    slashes = '//' if test_path.startswith('/') else '///'
    return f'file:{slashes}{test_path}'


def get_test_src_path(file_path: str) -> str:
    return os.path.join(__TEST_SRC_DIR, file_path)


def delete_saved_files(result_set: ElementResultSet, test: Callable[[str], bool] = None):
    for element_name in result_set.keys():
        result_list: list[ActionResult] = result_set.get(element_name)
        __delete_file_results(result_list, test)


def __delete_file_results(result_list: list[ActionResult], test: Callable[[str], bool] = None):
    for r in result_list:
        file = r.get_result()
        if file is None or not isinstance(file, str) or os.path.sep not in file or '/' not in file:
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

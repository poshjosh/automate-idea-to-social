import logging
from typing import TypeVar, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])


class WebDriverCreator:
    @staticmethod
    def create(config: dict[str, any], agent_config: dict[str, any] = None) -> WEB_DRIVER:
        chrome_config = config['browser']['chrome']
        executable_path: str = chrome_config.get('executable-path')
        option_args: list[str] = chrome_config['options']['args']
        preferences = {}
        preferences.update(chrome_config.get('prefs', {}))
        if agent_config is not None:
            preferences.update(agent_config.get('browser', {}).get('chrome', {}).get('prefs', {}))
        remote_dvr_location: str = config['selenium.webdriver.url'] \
            if 'selenium.webdriver.url' in config else None
        return WebDriverCreator.__create(
            executable_path, option_args, preferences, remote_dvr_location)

    @staticmethod
    def __create(executable_path: str,
           option_args: list[str],
           prefs: dict[str, str],
           remote_browser_location: str = '') -> WEB_DRIVER:
        logger.debug(f'Will create browser with\nprefs: {prefs}\noptions: {option_args}')
        options = Options()
        if option_args is not None:
            for arg in option_args:
                if arg is None or arg == '':
                    continue
                options.add_argument("--" + arg)
        if prefs is not None:
            options.add_experimental_option("prefs", prefs)
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        if remote_browser_location is None or remote_browser_location == '':
            service = webdriver.ChromeService(executable_path=executable_path)
            return webdriver.Chrome(options=options, service=service)

        return webdriver.Remote(options=options)

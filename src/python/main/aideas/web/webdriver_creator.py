import logging
import os
from typing import TypeVar, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

from ..env import Env

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])


class WebDriverCreator:
    @staticmethod
    def create(config: dict[str, any], agent_name: str) -> WEB_DRIVER:
        chrome_config = config['browser']['chrome']

        executable_path: str = Env.get_path(Env.BROWSER_CHROME_EXECUTABLE_PATH)

        option_args: list[str] = chrome_config.get('options', {}).get('args', [])
        env_opt_args: list[str] = [
            Env.get_path(Env.BROWSER_CHROME_OPTIONS_ARGS_USER_DATA_DIR),
            Env.get_value(Env.BROWSER_CHROME_OPTIONS_ARGS_PROFILE_DIRECTORY)
        ]
        for env_opt_arg in env_opt_args:
            if not env_opt_arg:
                continue
            if env_opt_arg in option_args:
                option_args[option_args.index(env_opt_arg)] = env_opt_arg
            else:
                option_args.append(env_opt_arg)

        preferences = {}
        preferences.update(chrome_config.get('prefs', {}))
        output_dir = os.path.join(Env.require_path(Env.VIDEO_OUTPUT_DIR), agent_name)
        if os.path.exists(output_dir) is False:
            os.makedirs(output_dir)
            logger.debug(f"Created dirs: {output_dir}")
        preferences.update({'download.default_directory': output_dir})

        undetected: bool = chrome_config.get('undetected', False)

        remote_dvr_location: str = config['selenium.webdriver.url'] \
            if 'selenium.webdriver.url' in config else None

        return WebDriverCreator.__create(
            executable_path, option_args, preferences, undetected, remote_dvr_location)

    @staticmethod
    def __create(executable_path: str,
                 option_args: list[str],
                 prefs: dict[str, str],
                 undetected: bool = False,
                 remote_browser_location: str = '') -> WEB_DRIVER:
        logger.debug(f'Will create browser with\nprefs: {prefs}\noptions: {option_args}')
        options = Options()
        if option_args is not None:
            for arg in option_args:
                if arg is None or arg == '':
                    continue
                options.add_argument("--" + arg)

        if prefs is not None and undetected is False:
            options.add_experimental_option("prefs", prefs)

        if remote_browser_location is None or remote_browser_location == '':

            if undetected:
                logger.debug("Undetected ChromeDriver will be used")
                # See https://github.com/ultrafunkamsterdam/undetected-chromedriver
                return uc.Chrome(options=options, use_subprocess=False)

            logger.debug("ChromeDriver will be used")
            service = webdriver.ChromeService(executable_path=executable_path)
            return webdriver.Chrome(options=options, service=service)

        logger.debug("Remote WebDriver will be used")
        return webdriver.Remote(options=options)

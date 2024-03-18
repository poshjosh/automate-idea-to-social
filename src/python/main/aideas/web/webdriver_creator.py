import logging
import os
from typing import TypeVar, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

from ..env import Env, get_path, get_value, require_path

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])


class WebDriverCreator:
    @staticmethod
    def create(config: dict[str, any], agent_name: str) -> WEB_DRIVER:
        chrome_config = config['browser']['chrome']

        executable_path: str = get_path(Env.BROWSER_CHROME_EXECUTABLE_PATH)

        option_args: list[str] = chrome_config.get('options', {}).get('args', [])
        use_profile: bool = chrome_config.get('use-profile', False)
        if use_profile:
            WebDriverCreator.__add_options_from_env(option_args)

        preferences = {}
        preferences.update(chrome_config.get('prefs', {}))
        WebDriverCreator.__add_prefs_from_env(preferences, agent_name)

        undetected: bool = chrome_config.get('undetected', False)

        remote_dvr_location: str = config['selenium.webdriver.url'] \
            if 'selenium.webdriver.url' in config else None

        return WebDriverCreator.__create(
            executable_path, option_args, preferences, undetected, remote_dvr_location)

    @staticmethod
    def __add_options_from_env(add_to: list[str]):
        env_opt_args: list[str] = [
            get_path(Env.BROWSER_CHROME_OPTIONS_ARGS_USER_DATA_DIR),
            get_value(Env.BROWSER_CHROME_OPTIONS_ARGS_PROFILE_DIRECTORY)
        ]
        for env_opt_arg in env_opt_args:
            if not env_opt_arg:
                continue
            if env_opt_arg in add_to:
                add_to[add_to.index(env_opt_arg)] = env_opt_arg
            else:
                add_to.append(env_opt_arg)

    @staticmethod
    def __add_prefs_from_env(add_to: dict[str, str], agent_name: str):
        output_dir = os.path.join(require_path(Env.VIDEO_OUTPUT_DIR), agent_name)
        if os.path.exists(output_dir) is False:
            os.makedirs(output_dir)
            logger.debug(f"Created dirs: {output_dir}")
        add_to.update({'download.default_directory': output_dir})

    @staticmethod
    def __create(executable_path: str,
                 option_args: list[str],
                 prefs: dict[str, str],
                 undetected: bool = False,
                 remote_browser_location: str = '') -> WEB_DRIVER:
        """
        Options are ignored for un-detected ChromeDriver
        :param executable_path:
        :param option_args: The options
        :param prefs: The preferences
        :param undetected: If undetected ChromeDriver should be used.
        :param remote_browser_location: The location if a remote browser is to be used.
        :return: The newly created webdriver.
        """
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
                #
                # options are ignored for un-detected ChromeDriver
                #
                logger.debug("Undetected ChromeDriver will be used")
                # See https://github.com/ultrafunkamsterdam/undetected-chromedriver
                return uc.Chrome(use_subprocess=False)

            logger.debug("ChromeDriver will be used")
            service = webdriver.ChromeService(executable_path=executable_path)
            return webdriver.Chrome(options=options, service=service)

        logger.debug("Remote WebDriver will be used")
        return webdriver.Remote(options=options)

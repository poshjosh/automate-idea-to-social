import logging
from typing import TypeVar, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

from .browser_options import chrome_options
from ..env import Env, get_path

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])


class WebDriverCreator:
    @staticmethod
    def create(config: dict[str, any], agent_name: str) -> WEB_DRIVER:

        options: Options = chrome_options(config, agent_name)

        chrome_config = config['browser']['chrome']

        executable_path: str = get_path(Env.BROWSER_CHROME_EXECUTABLE_PATH)

        undetected: bool = chrome_config.get('undetected', False)

        remote_dvr_location: str = config['SELENIUM_WEBDRIVER_URL'] \
            if 'SELENIUM_WEBDRIVER_URL' in config else None

        return WebDriverCreator.__create(executable_path, options, undetected, remote_dvr_location)

    @staticmethod
    def __create(executable_path: str,
                 options: Options,
                 undetected: bool = False,
                 remote_browser_location: str = '') -> WEB_DRIVER:
        """
        Options are ignored for un-detected ChromeDriver
        :param executable_path:
        :param options: The options
        :param undetected: If undetected ChromeDriver should be used.
        :param remote_browser_location: The location if a remote browser is to be used.
        :return: The newly created webdriver.
        """
        if remote_browser_location:
            logger.debug("Remote WebDriver will be used")
            return webdriver.Remote(options=options)

        if undetected is True:
            #
            # options are ignored for un-detected ChromeDriver
            #
            logger.debug("Undetected ChromeDriver will be used")
            # See https://github.com/ultrafunkamsterdam/undetected-chromedriver
            driver = uc.Chrome(use_subprocess=False)
            try:
                driver.maximize_window()
            except Exception as ex:
                logger.warning(f"Failed to maximize window: {ex}")
            return driver

        logger.debug("ChromeDriver will be used")
        service = webdriver.ChromeService(executable_path=executable_path)
        return webdriver.Chrome(options=options, service=service)

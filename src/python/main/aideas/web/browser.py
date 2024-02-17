import logging
from typing import Callable, Union, Literal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import D, T
from selenium.webdriver.support import expected_conditions as WaitCondition

from .login_ui_selector import LoginUiSelector
from .login_ui import LoginUi
from .selector_by_pivot import SelectorByPivot
from .web_functions import execute_for_bool, wait_until

logger = logging.getLogger(__name__)


class Browser:
    def __init__(self,
                 option_args: list[str],
                 remote_browser_location: str = '',
                 wait_timeout_seconds: float = 20):
        self.__webdriver = _create_webdriver(option_args, remote_browser_location)
        self.__wait_timeout_seconds = wait_timeout_seconds

    @staticmethod
    def create(config):
        chrome_config = config['browser']['chrome']
        option_args = chrome_config['options']['args']
        remote_dvr = config['selenium.webdriver.url'] if 'selenium.webdriver.url' in config else None
        return Browser(option_args, remote_dvr, chrome_config["wait-timeout-seconds"])

    def login(self, link: str, xpath_config: dict[str, str], username: str, password: str) -> bool:
        login_ui_array = LoginUiSelector().select(self.__webdriver, link, xpath_config)
        logger.debug(f'Will login to: {link}')
        for login_ui in login_ui_array:
            success = LoginUi(login_ui).login(username, password)
            # TODO - For pictory the link does not change after login,
            #  so we need to find a better way to determine success
            if success is True:  # and link != self.__webdriver.current_url:
                logger.debug(f'Login successful; link: {link}')
                return True
        logger.warning(f'Login failed; link: {link}')
        return False

    def load_page_body(self, link: str, result_if_none: WebElement) -> WebElement:
        try:
            self.__webdriver.get(link)
            return wait_until(
                self.__webdriver,
                self.__wait_timeout_seconds,
                WaitCondition.presence_of_element_located((By.TAG_NAME, "body")))
        except Exception as e:
            logger.warning(f'Failed to load page body: {link}; {e}')
            return result_if_none

    def select_element_by_pivot(self,
                                web_obj: D,
                                pivot_element_xpath: str,
                                search_root_element_xpath: str,
                                element_filter: Callable[[WebElement], bool],
                                result_if_none: WebElement) -> WebElement:

        return SelectorByPivot(web_obj, self.__wait_timeout_seconds).select(
            pivot_element_xpath,
            search_root_element_xpath,
            element_filter, result_if_none)

    def quit(self):
        self.__webdriver.quit()


def _create_webdriver(option_args: list[str], remote_browser_location: str = '') -> webdriver:
    chrome_options = Options()
    if option_args is not None:
        for arg in option_args:
            if arg is None or arg == '':
                continue
            chrome_options.add_argument("--" + arg)
    logger.debug(f'Will create browser with options: {chrome_options}')

    if remote_browser_location is None or remote_browser_location == '':
        return webdriver.Chrome(options=chrome_options)

    return webdriver.Remote(remote_browser_location, options=chrome_options)

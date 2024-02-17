import logging
from typing import Callable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

from .login_ui_selector import LoginUiSelector
from .login_ui import LoginUi
from .selector_by_pivot import SelectorByPivot
from .web_functions import execute_for_bool

logger = logging.getLogger(__name__)


class Browser:
    def __init__(
            self, option_args: list[str], remote_browser_location: str = ''):
        self.__webdriver = _create_webdriver(option_args, remote_browser_location)

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

    def open(self, link: str) -> bool:
        return execute_for_bool(lambda arg: self.__webdriver.get(arg), link)

    def select_element_by_pivot(self,
                                pivot_element_xpath: str,
                                start_at_nth_ancestor: int,
                                element_filter: Callable[[WebElement], bool],
                                result_if_none: WebElement) -> WebElement:
        return SelectorByPivot(self.__webdriver).select(
            pivot_element_xpath, start_at_nth_ancestor, element_filter, result_if_none)

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

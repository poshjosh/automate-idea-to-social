import logging

from selenium.webdriver.remote.webelement import WebElement

from ..setup.login_credentials import LoginCredentials
from ..web.browser import Browser
from ..web.web_functions import is_button, execute_for_bool

logger = logging.getLogger(__name__)


class PictoryAgent:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def run(self, config: dict[str, any]) -> bool:
        logger.debug("Pictory Agent started")
        success = _login(self.__browser, config['login'])
        if success is not True:
            return False
        success = _open_script_input(self.__browser, config['text-input'])
        if success is not True:
            return False
        return True


def _login(browser: Browser, config: dict[str, any]) -> bool:
    login_credentials = LoginCredentials()
    return browser.login(
        config['url'], config['xpath'],
        login_credentials.get_username(), login_credentials.get_password())


def _open_script_input(browser: Browser, config: dict[str, any]) -> bool:
    success: bool = browser.open(config['url'])
    if success is False:
        return False
    pivot_config: dict = config['pivot']
    selected: WebElement = browser.select_element_by_pivot(
        pivot_config['xpath'], pivot_config['start-at-nth-ancestor'],
        lambda element: is_button(element), None)
    if selected is None:
        return False
    return execute_for_bool(lambda arg: arg.click(), selected)

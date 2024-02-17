import logging
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class LoginUi:
    def __init__(self, elements_dict: dict[str, WebElement]):
        self.__username_input = elements_dict['username']
        self.__password_input = elements_dict['password']
        self.__submit_input = elements_dict['submit']

    def login(self, username: str, password: str) -> bool:
        if (self.__username_input is None
                or self.__password_input is None
                or self.__submit_input is None):
            return False
        try:
            self.__username_input.send_keys(username)
            self.__password_input.send_keys(password)
            self.__submit_input.click()
        except Exception as ex:
            logging.error(f'Error: {ex}')
            return False
        else:
            return True
import logging
import os
import pickle

from selenium.common.exceptions import InvalidCookieDomainException, UnableToSetCookieException, \
    NoSuchWindowException

logger = logging.getLogger(__name__)


class BrowserCookieStore:
    def __init__(self, webdriver, domain: str):
        if webdriver is None:
            raise ValueError("webdriver cannot be None")
        dir_path = os.path.join(os.getcwd(), 'resources', 'agent', domain, "cookies.pkl")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.__webdriver = webdriver
        self.__cookie_path = os.path.join(dir_path, "cookies.pkl")

    def save(self):
        cookies: list[dict] = self.__webdriver.get_cookies()
        logger.debug(f"Saving cookies: {cookies}")
        if len(cookies) == 0:
            return
        with open(self.__cookie_path, 'wb') as file:
            pickle.dump(cookies, file)

    def load(self):
        cookies: list[dict] = []
        try:
            with open(self.__cookie_path, 'rb') as file:
                cookies = pickle.load(file)
                logger.debug(f'Loaded cookies: {cookies}')
        except EOFError as ignored:
            logger.debug("No cookies to load")
        try:
            for cookie in cookies:
                self.__webdriver.add_cookie(cookie)
        except InvalidCookieDomainException as ignored:
            logger.debug(f'Cookies do not match domain: {self.current_url()}')
        except UnableToSetCookieException as ignored:
            logger.debug(f'Unable to set cookies: {cookies}')

    def current_url(self, result_if_none: str = None) -> str:
        try:
            return self.__webdriver.current_url
        except NoSuchWindowException as ignored:
            return result_if_none

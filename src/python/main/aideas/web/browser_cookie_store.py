import logging
import os
import pickle

from selenium.common.exceptions import InvalidCookieDomainException

logger = logging.getLogger(__name__)


class BrowserCookieStore:
    @staticmethod
    def create_file(path):
        basedir = os.path.dirname(path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        if not os.path.exists(path):
            with open(path, 'a'):
                os.utime(path, None)

    def __init__(self, webdriver, domain: str):
        if webdriver is None:
            raise ValueError("webdriver cannot be None")
        self.__webdriver = webdriver
        self.__cookie_path = os.path.join(os.getcwd(), 'resources', 'agent', domain, "cookies.pkl")
        self.create_file(self.__cookie_path)

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
            logger.debug(f'Cookies do not match domain: {self.__webdriver.current_url}')
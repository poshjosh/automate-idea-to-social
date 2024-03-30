import logging
import os
import pickle

from selenium.common.exceptions import InvalidCookieDomainException, UnableToSetCookieException, \
    NoSuchWindowException

logger = logging.getLogger(__name__)


class BrowserCookieStore:
    def __init__(self, webdriver, file):
        if webdriver is None:
            raise ValueError("webdriver cannot be None")
        dir_path = os.path.dirname(file)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.__webdriver = webdriver
        self.__cookie_path = file

    def save(self):
        cookies: list[dict] = self.__webdriver.get_cookies()
        logger.debug(f"Saving {0 if not cookies else len(cookies)} cookies to {self.__cookie_path}")
        if len(cookies) == 0:
            return
        with open(self.__cookie_path, 'wb') as file:
            pickle.dump(cookies, file)

    def load(self):
        if not os.path.exists(self.__cookie_path):
            return
        cookies: list[dict] = []
        try:
            with open(self.__cookie_path, 'rb') as file:
                cookies = pickle.load(file)
                logger.debug(f'Read {0 if not cookies else len(cookies)} '
                             f'cookies from {self.__cookie_path}')
        except EOFError:
            logger.debug(f"No cookies in file: {self.__cookie_path}")
        try:
            for cookie in cookies:
                self.__webdriver.add_cookie(cookie)
            logger.debug(f'Added {0 if not cookies else len(cookies)} '
                         f'cookies for {self.current_url()}')
        except InvalidCookieDomainException:
            logger.warning(f'Cookies do not match domain: {self.current_url()}')
        except UnableToSetCookieException:
            logger.warning(f'Unable to set cookies: {cookies}')

    def current_url(self, result_if_none: str = None) -> str:
        try:
            return self.__webdriver.current_url
        except NoSuchWindowException:
            return result_if_none

import logging
import os
import pickle

logger = logging.getLogger(__name__)


class BrowserCookieStore:
    def __init__(self, webdriver):
        if webdriver is None:
            raise ValueError("webdriver cannot be None")
        self.__webdriver = webdriver
        self.__cookie_path = os.getcwd() + '/resources/cookies.pkl'
        self.__has_cookies = False

    def save(self):
        # if (os.path.exists(self.__cookie_path) is False):
        #     pass
        cookies: list[dict] = self.__webdriver.get_cookies()
        logger.debug(f"Saving cookies: {cookies}")
        if len(cookies) == 0:
            return
        with open(self.__cookie_path, 'wb') as file:
            pickle.dump(cookies, file)
            self.__has_cookies = True

    def load(self):
        if self.__has_cookies is False:
            return
        with open(self.__cookie_path, 'rb') as file:
            cookies = pickle.load(file)
            logger.debug(f"Loaded cookies: {cookies}")
            for cookie in cookies:
                self.__webdriver.add_cookie(cookie)

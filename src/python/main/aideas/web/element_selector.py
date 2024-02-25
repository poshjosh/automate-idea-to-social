import logging
from typing import List, Union, Tuple

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait, D

from .browser_cookie_store import BrowserCookieStore
from .element_search_config import ElementSearchConfig

logger = logging.getLogger(__name__)


class ElementSelector:
    @staticmethod
    def of(webdriver, wait_timeout_seconds: float = 20) -> 'ElementSelector':
        return ElementSelector(webdriver, wait_timeout_seconds, BrowserCookieStore(webdriver))

    def __init__(self,
                 webdriver,
                 wait_timeout_seconds: float,
                 browser_cookie_store: BrowserCookieStore):
        self.__webdriver = webdriver
        self.__select_by = By.XPATH
        self.__wait_timeout_seconds = wait_timeout_seconds
        self.__browser_cookie_store = browser_cookie_store

    def with_timeout(self, timeout: float) -> 'ElementSelector':
        if timeout == self.__wait_timeout_seconds:
            return self
        return ElementSelector(self.__webdriver, timeout, self.__browser_cookie_store)

    def select_element(self,
                       root_element: WebElement,
                       element_name: str,
                       search_config: ElementSearchConfig) -> WebElement:
        if root_element is None:
            raise ValueError('root element for searching is None')

        search_from: str = search_config.get_search_from()
        search_for: str = search_config.get_search_for()

        if search_from is None or search_from == '':
            if search_for is None or search_for == '':
                raise ValueError(
                    f'search_from and search_for are both None or empty for {element_name}')
            search_from_element = root_element
        else:
            search_from_element = self.__wait_until_element_is_clickable(
                root_element, element_name, (self.__select_by, search_from))

        if search_from_element is None:
            raise ValueError(f'For {element_name} search_from is not valid: {search_from}')

        if search_for is None or search_for == '':
            return search_from_element

        selected = self.__wait_until_element_is_clickable(
            search_from_element, element_name, (self.__select_by, search_for))
        if selected is not None:
            return selected
        else:
            raise ValueError(f"Failed to select {element_name} element, "
                             f"current url: {self.__webdriver.current_url}.")

    def load_page_bodies(self, link: str) -> List[WebElement]:
        page_newly_loaded: bool = self.__load_page(link)
        page_bodies: List[WebElement] = self.__select_page_bodies()
        # We wait till the body elements are located
        # Then we save cookies, if the page is newly loaded.
        if page_newly_loaded:
            self.__browser_cookie_store.save()
        return page_bodies

    def get_webdriver(self):
        return self.__webdriver

    def get_wait_timeout_seconds(self):
        return self.__wait_timeout_seconds

    def get_browser_cookie_store(self):
        return self.__browser_cookie_store

    def __load_page(self, link: str) -> bool:
        if link == self.__webdriver.current_url:
            logger.debug(f'Already at: {link}')
            return False
        self.__browser_cookie_store.load()
        logger.debug(f'Opening page: {link}')
        self.__webdriver.get(link)
        return True

    def __select_page_bodies(self) -> List[WebElement]:
        body_elements: List[WebElement] = self.__webdriver.find_elements(By.TAG_NAME, 'body')
        if len(body_elements) == 0:
            raise ValueError(f'No body elements found for {self.__webdriver.current_url}')

        return body_elements

    def __wait_until_element_is_clickable(self,
                                          root_element: D,
                                          element_name: str,
                                          mark: Union[WebElement, Tuple[str, str]]) -> WebElement:
        try:
            return WebDriverWait(root_element, self.__wait_timeout_seconds).until(
                WaitCondition.element_to_be_clickable(mark))
        except TimeoutException:
            logger.debug(
                f'Timed out selecting {element_name}, '
                f'current url: {self.__webdriver.current_url}.')
            return root_element.find_element(*mark)

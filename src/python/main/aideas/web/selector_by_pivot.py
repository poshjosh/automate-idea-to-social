import logging
from typing import Callable
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import D

from ..web.web_functions import select_first, wait_until

logger = logging.getLogger(__name__)


class SelectorByPivot:
    def __init__(self, web_obj: D, wait_timeout_seconds: float):
        self.__web_obj = web_obj
        self.__wait_timeout_seconds = wait_timeout_seconds

    def select(self,
               pivot_element_xpath: str,
               search_root_element_xpath: str,
               element_filter: Callable[[WebElement], bool],
               result_if_none: WebElement) -> WebElement:

        pivot_elements: list[WebElement] = wait_until(
            self.__web_obj,
            self.__wait_timeout_seconds,
            WaitCondition.presence_of_all_elements_located((By.XPATH, pivot_element_xpath)))
        if len(pivot_elements) == 0:
            logger.warning(f"Not found. page -> xpath: {pivot_element_xpath}")
            return result_if_none

        for pivot_element in pivot_elements:

            search_root = pivot_element.find_element(By.XPATH, search_root_element_xpath)
            # search_root: WebElement = wait_until(
            #     pivot_element,
            #     self.__wait_timeout_seconds,
            #     WaitCondition.presence_of_element_located((By.XPATH, search_root_element_xpath)))
            if search_root is None:
                logger.warning(f"Not found. pivot_element -> xpath: {search_root_element_xpath}")
                continue

            selected = select_first(search_root, element_filter, result_if_none)

            if selected != result_if_none:
                logger.debug("Successfully selected an element by pivot")
                return selected

        logger.warning("Failed to select an element by pivot")
        return result_if_none



import logging
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class SelectorByPivot:
    def __init__(self, webdriver):
        self.__webdriver = webdriver

    def select(self,
               pivot_element_xpath: str,
               start_at_nth_ancestor: int,
               element_filter: Callable[[WebElement], bool],
               result_if_none: WebElement) -> WebElement:

        pivot_elements = self.__webdriver.find_elements(By.XPATH, pivot_element_xpath)
        if len(pivot_elements) == 0:
            return result_if_none

        for pivot_element in pivot_elements:

            nth_ancestor = pivot_element if start_at_nth_ancestor < 1 else (
                _get_nth_ancestor(pivot_element, start_at_nth_ancestor))

            selected = _select_first_button(nth_ancestor, element_filter, result_if_none)

            if selected != result_if_none:
                logger.debug("Successfully selected an element by pivot")
                return selected

        logger.warning("Failed to select an element by pivot")
        return result_if_none


def _get_nth_ancestor(element: WebElement, levels_above: int) -> WebElement:
    return element.find_element(By.XPATH, f'/ancestor::*[{levels_above}]')


def _get_nth_ancestor1(element: WebElement, n: int) -> WebElement:
    for _ in range(n):
        element = element.find_element(By.XPATH, '..')
    return element


def _select_first_button(element : WebElement,
                         test: Callable[[WebElement], bool],
                         result_if_none: WebElement) -> WebElement:
    if test(element) is True:
        return element
    child_elements = element.find_elements(By.XPATH, '*')
    for child_element in child_elements:
        if test(child_element) is True:
            return child_element
        else:
            return _select_first_button(child_element, test, result_if_none)
    return result_if_none


def _is_button(element: WebElement) -> bool:
    if (element.tag_name == 'button'
            or element.get_attribute('type') == 'button'
            or element.get_attribute('type') == 'submit'):
        return True
    return False

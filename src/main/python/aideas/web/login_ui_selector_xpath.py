import logging
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .web_functions import get_web_page_bodies

logger = logging.getLogger(__name__)


class LoginUiSelectorXpath:

    def select(self, webdriver,
               link: str,
               xpath_config: dict[str, str]) -> list[dict[str, WebElement]]:

        body_inputs: List[WebElement] = get_web_page_bodies(webdriver, link)

        login_uis: list[dict] = []

        for body_input in body_inputs:
            login_ui = _select(body_input, xpath_config, {})
            if login_ui is not None and login_ui != {}:
                login_uis.append(login_ui)

        return login_uis


def _select(body_input: WebElement,
            xpath_config: dict[str, str],
            result_if_none: dict[str, WebElement]) -> dict[str, WebElement]:
    forms = body_input.find_elements(By.XPATH, xpath_config['form'])
    if len(forms) == 0:
        return result_if_none
    for form in forms:
        try:
            selected = _select_child(form, xpath_config, result_if_none)
            if selected == result_if_none:
                continue
        except Exception as ex:
            logger.debug(f'Error: {ex}')
            continue
        else:
            return selected
    return result_if_none


def _select_child(element: WebElement,
                  xpath_config: dict[str, str],
                  result_if_none: dict[str, WebElement]) -> dict[str, WebElement]:
    username_input = element.find_element(By.XPATH, xpath_config['username'])
    password_input = element.find_element(By.XPATH, xpath_config['password'])
    submit_input = element.find_element(By.XPATH, xpath_config['submit'])
    if username_input is None or password_input is None or submit_input is None:
        return result_if_none
    return {'username': username_input, 'password': password_input, 'submit': submit_input}

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .web_functions import get_web_page_bodies

logger = logging.getLogger(__name__)


class LoginUiSelectorBrute:

    def select(self, webdriver, link: str) -> list[dict]:

        body_inputs = get_web_page_bodies(webdriver, link)

        login_uis = []

        for body_input in body_inputs:
            _collect_inputs_recursively(login_uis, body_input)

        logger.debug("Found %d login UIs: ", len(login_uis))

        return login_uis

def _collect_inputs_recursively(login_uis: list[dict], element: WebElement):

    _collect_inputs(login_uis, element)

    child_elements = element.find_elements(By.CSS_SELECTOR, '*')
    for child_element in child_elements:
        _collect_inputs_recursively(login_uis, child_element)


def _collect_inputs(login_uis: list[dict], element: WebElement):

    if element is None:
        return

    if element.tag_name != 'input':
        return

    input_type = element.get_attribute('type')
    if input_type is None or input_type == '':
        return

    last_login_ui = {} if len(login_uis) == 0 else login_uis[-1]
    #print("Last login UI: " + str(last_login_ui))

    if input_type == 'text':
        if last_login_ui.get('password', None) is None:
            # Replace last login UI if it has no password input
            #print("Updating username: " + str(element))
            last_login_ui['username'] = element
        else:
            # Add new login UI with username input
            #print("Adding input: " + str(element))
            login_uis.append({'username': element})
    elif input_type == 'password':
        if last_login_ui.get('username', None) is not None:
            # Add password input to login UI which has existing username input
            print("Adding password: " + str(element))
            last_login_ui['password'] = element
    elif input_type == 'submit' or input_type == 'button':
        if last_login_ui.get('password', None) is not None:
            # Add submit input to login UI which has existing username & password inputs
            print("Adding submit: " + str(element))
            last_login_ui['submit'] = element

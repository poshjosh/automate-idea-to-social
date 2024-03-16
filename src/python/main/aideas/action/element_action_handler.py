import logging
import time
from enum import unique
from typing import Tuple

from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement

from .action_handler import execute_for_result, BaseActionId
from .browser_action_handler import BrowserActionHandler, WEB_DRIVER
from ..action.action import Action
from ..action.action_result import ActionResult
from ..web.reloadable_web_element import ReloadableWebElement

logger = logging.getLogger(__name__)


@unique
class ElementActionId(BaseActionId):
    CLEAR_TEXT = ('clear_text', False)
    CLICK = ('click', False)
    CLICK_AND_HOLD = ('click_and_hold', False)
    CLICK_AND_HOLD_CURRENT_POSITION = ('click_and_hold_current_position', False)
    ENTER = ('enter', False)
    ENTER_TEXT = ('enter_text', False)
    GET_ATTRIBUTE = 'get_attribute'
    GET_TEXT = 'get_text'
    IS_DISPLAYED = 'is_displayed'
    MOVE_TO_CENTER_OFFSET = ('move_to_center_offset', False)
    MOVE_TO_ELEMENT = ('move_to_element', False)
    RELEASE = ('release', False)
    SEND_KEYS = ('send_keys', False)


class ElementActionHandler(BrowserActionHandler):
    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        try:
            return BrowserActionHandler.to_action_id(action)
        except Exception:
            return ElementActionId(action)

    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float):
        super().__init__(
            web_driver, wait_timeout_seconds)

    def with_timeout(self, timeout: float) -> 'ElementActionHandler':
        if timeout == self.get_wait_timeout_seconds():
            return self
        return ElementActionHandler(self.get_web_driver(), timeout)

    def execute_on(self, action: Action, element: WebElement) -> ActionResult:
        key = action.get_name_without_negation() if action.is_negation() else action.get_name()
        try:
            if isinstance(element, ReloadableWebElement):
                # We use the actual web element for the action
                # When we used the ReloadableWebElement, the action fails with message:
                # TypeError: Object of type ReloadableWebElement is not JSON serializable
                element = element.get_delegate()

            result = self._execute_on(key, action, element)

        except StaleElementReferenceException as ex:
            if isinstance(element, ReloadableWebElement):
                logger.warning('Element is stale. Attempting to reload')
                element = element.reload()
                logger.debug(f'Retrying action after reloading element: {action}')
                result = self._execute_on(key, action, element)
            else:
                raise ex
        if action.is_negation():
            result = result.flip()
        return result

    def _execute_on(self, key: str, action: Action, element: WebElement) -> ActionResult:
        driver = self.get_web_driver()
        # TODO - Use ElementActionId instead of str literals
        if key == ElementActionId.CLEAR_TEXT.value:
            def clear_text(tgt: WebElement):
                tgt.send_keys(Keys.CONTROL, 'a')
                tgt.send_keys(Keys.DELETE)
                tgt.clear()  # May not work under certain conditions, so we try the following

            result = execute_for_result(clear_text, element, action)
        elif key == 'click':
            result = execute_for_result(lambda arg: arg.click(), element, action)
        elif key == 'click_and_hold':
            def click_and_hold(tgt: WebElement):
                ActionChains(driver).click_and_hold(tgt).perform()

            result = execute_for_result(click_and_hold, element, action)
        elif key == 'click_and_hold_current_position':
            def click_and_hold_current_position(_: WebElement):
                ActionChains(driver).click_and_hold(None).perform()

            result = execute_for_result(click_and_hold_current_position, element, action)
        elif key == 'enter':
            result = execute_for_result(lambda arg: arg.send_keys(Keys.ENTER), element, action)
        elif key == 'enter_text':
            text: str = ' '.join(action.get_args())
            result = execute_for_result(lambda arg: arg.send_keys(text), element, action)
        elif key == 'get_attribute':
            attr_name = action.get_first_arg()
            result = execute_for_result(lambda arg: element.get_attribute(arg), attr_name, action)
        elif key == 'get_text':
            text = element.text
            result = ActionResult(action, True, text if not text else text.strip())
        elif key == 'is_displayed':
            success = element.is_displayed()
            result = ActionResult(action, success, success)
        elif key == 'move_to_center_offset':
            offset: Tuple[int, int] = self.__get_offset(action.get_args())

            def move_to_center_offset(tgt: WebElement):
                ActionChains(driver).move_to_element_with_offset(
                    tgt, offset[0], offset[1]).perform()

            result = execute_for_result(move_to_center_offset, element, action)
        elif key == 'move_to_element':
            def move_to_element(tgt: WebElement):
                ActionChains(driver).move_to_element(tgt).perform()

            result = execute_for_result(move_to_element, element, action)
        elif key == 'release':
            def release(tgt: WebElement):
                ActionChains(driver).release(tgt).perform()

            result = execute_for_result(release, element, action)
        elif key == 'send_keys':
            def send_keys(txt: str):
                for char in txt:
                    element.send_keys(char)
                    time.sleep(0.5)
                return txt

            result = execute_for_result(send_keys, ' '.join(action.get_args()), action)
        else:
            return super()._execute(key, action)  # Success state has already been printed
        logger.debug(f'{result}')
        return result

    @staticmethod
    def __get_offset(args: list[str]) -> Tuple[int, int]:
        return int(args[0]), int(args[1])

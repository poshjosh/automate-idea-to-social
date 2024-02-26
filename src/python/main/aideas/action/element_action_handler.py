import logging
from typing import Callable, Tuple

from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from .browser_action_handler import BrowserActionHandler, WEB_DRIVER
from ..action.action import Action
from ..action.action_result import ActionResult

logger = logging.getLogger(__name__)


class ElementActionHandler(BrowserActionHandler):
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
        name: str = action.get_name()
        driver = self.get_web_driver()
        if name == 'click':
            result = self.__execute_for_result(lambda arg: arg.click(), element, action)
        elif name == 'click_and_hold':
            def click_and_hold(tgt: WebElement):
                ActionChains(driver).click_and_hold(tgt).perform()

            result = self.__execute_for_result(click_and_hold, element, action)
        elif name == 'click_and_hold_current_position':
            def click_and_hold_current_position(tgt: WebElement):
                ActionChains(driver).click_and_hold(None).perform()

            result = self.__execute_for_result(click_and_hold_current_position, element, action)
        elif name == 'enter_text':
            text: str = ' '.join(action.get_args())
            result = self.__execute_for_result(lambda arg: arg.send_keys(text), element, action)
        elif name == 'get_text':
            result = ActionResult(action, True, element.text)
        elif name == 'is_displayed':
            success = element.is_displayed()
            result = ActionResult(action, success, success)
        elif name == 'move_to_center_offset':
            offset: Tuple[int, int] = self.__get_offset(action.get_args())

            def move_to_center_offset(tgt: WebElement):
                ActionChains(driver).move_to_element_with_offset(
                    tgt, offset[0], offset[1]).perform()

            result = self.__execute_for_result(move_to_center_offset, element, action)
        elif name == 'move_to_element':
            def move_to_element(tgt: WebElement):
                ActionChains(driver).move_to_element(tgt).perform()

            result = self.__execute_for_result(move_to_element, element, action)
        elif name == 'release':
            def release(tgt: WebElement):
                ActionChains(driver).release(tgt).perform()

            result = self.__execute_for_result(release, element, action)
        else:
            return super().execute(action)  # Success state has already been printed
        logger.debug(f"{result}")
        return result

    def __execute_for_result(self,
                             func: Callable[[any], any],
                             arg: any,
                             action: Action) -> ActionResult:
        result = None
        try:
            result = func(arg)
        except Exception as ex:
            logger.warning(f'{str(ex)}')
            return ActionResult(action, False, result)
        else:
            return ActionResult(action, True, result)

    def __get_offset(self, args: list[str]) -> Tuple[int, int]:
        return int(args[0]), int(args[1])

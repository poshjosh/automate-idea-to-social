import logging
from typing import TypeVar, Union

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as WaitCondition
from selenium.webdriver.support.wait import WebDriverWait

from ..action.action import Action
from ..action.action_handler import ActionHandler
from ..action.action_result import ActionResult

logger = logging.getLogger(__name__)

WEB_DRIVER = TypeVar("WEB_DRIVER", bound=Union[webdriver.Chrome, webdriver.Remote])
ALERT_ACTION = TypeVar("ALERT_ACTION", bound=Union['accept', 'dismiss'])


class BrowserActionHandler(ActionHandler):
    def __init__(self,
                 web_driver: WEB_DRIVER,
                 wait_timeout_seconds: float):
        self.__web_driver = web_driver
        self.__wait_timeout_seconds = wait_timeout_seconds

    def with_timeout(self, timeout: float) -> 'BrowserActionHandler':
        if timeout == self.__wait_timeout_seconds:
            return self
        return BrowserActionHandler(self.__web_driver, timeout)

    def execute(self, action: Action) -> ActionResult:
        name: str = action.get_name()
        if name.endswith("alert"):  # accept_alert|dismiss_alert
            result = self.__handle_alert(action)
        else:
            return super().execute(action)
        logger.debug(f"{result}")
        return result

    def get_web_driver(self) -> WEB_DRIVER:
        return self.__web_driver

    def get_wait_timeout_seconds(self) -> float:
        return self.__wait_timeout_seconds

    def __handle_alert(self, action: Action) -> ActionResult:
        how: str = action.get_name().split("_")[0]  # accept|dismiss
        value: str = action.get_first_arg('')
        timeout = self.__wait_timeout_seconds if (value is None or value == '') else float(value)
        try:
            WebDriverWait(self.__web_driver, timeout).until(
                WaitCondition.alert_is_present())
            alert: Alert = self.__web_driver.switch_to().alert()
            if how == 'accept':
                alert.accept()
            elif how == 'dismiss':
                alert.dismiss()
            else:
                return ActionResult(action, False, f"Unsupported: {action}")
        except TimeoutException:
            logger.debug(f"Timed out waiting for alert. {action}")

        return ActionResult(action, True)
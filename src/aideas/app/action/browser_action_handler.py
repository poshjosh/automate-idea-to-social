import time

import logging
import os.path
from enum import unique
from selenium.webdriver.common.by import By
from typing import TypeVar, Union

from selenium.common import TimeoutException, NoAlertPresentException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as wait_condition
from selenium.webdriver.support.wait import WebDriverWait

from pyu.io.file import create_file, write_content

from ..action.action import Action
from ..action.action_handler import ActionHandler, BaseActionId, ActionId
from ..action.action_result import ActionResult
from ..config import RunArg
from ..env import get_cookies_file, get_cached_results_file
from ..run_context import RunContext
from ..web.element_selector import ElementSelector
from ..web.webdriver_creator import WEB_DRIVER

logger = logging.getLogger(__name__)

ALERT_ACTION = TypeVar("ALERT_ACTION", bound=Union['accept', 'dismiss'])


@unique
class BrowserActionId(BaseActionId):
    ACCEPT_ALERT = ('accept_alert', False)
    ASK_FOR_HELP = ActionId.ASK_FOR_HELP
    BROWSE_TO = ('browse_to', False)
    DELETE_COOKIES = ('delete_cookies', False)
    DISABLE_CURSOR = ('disable_cursor', False)
    DISMISS_ALERT = ('dismiss_alert', False)
    ENABLE_CURSOR = ('enable_cursor', False)
    EXECUTE_SCRIPT = 'execute_script'
    MOVE_BY_OFFSET = ('move_by_offset', False)
    REFRESH = ('refresh', False)
    SAVE_SCREENSHOT = ('save_screenshot', True)
    SAVE_WEBPAGE = ('save_webpage', True)


class BrowserActionHandler(ActionHandler):
    @staticmethod
    def to_action_id(action: str) -> BaseActionId:
        try:
            return ActionHandler.to_action_id(action)
        except ValueError:
            return BrowserActionId(action)

    def __init__(self,
                 element_selector: ElementSelector,
                 wait_timeout_seconds: float):
        self.__element_selector = element_selector
        self.__wait_timeout_seconds = wait_timeout_seconds

    def with_timeout(self, timeout: float) -> 'BrowserActionHandler':
        if timeout == self.__wait_timeout_seconds:
            return self
        return self.__class__(self.__element_selector, timeout)

    def ask_for_help(self, action: Action) -> ActionResult:
        args = action.get_args_as_str_list()
        timeout = float(args[1]) if len(args) > 1 else self.get_default_help_timeout_seconds()
        message = f"After clicking OK, you have {timeout} seconds to help by doing the following: {args[0]}"

        web_driver = self.get_web_driver()
        BrowserActionHandler.__wait_till_page_loaded(web_driver)

        web_driver.execute_script("window.alert(\"" + message +"\");")
        WebDriverWait(web_driver, 10).until(wait_condition.alert_is_present())

        # When we used the logger, the message was masked, probably due to the word password.
        print("The following message should be displayed in the browser:\n", message)

        time.sleep(timeout)

        try:
            web_driver.switch_to.alert.dismiss()
            return ActionResult.failure(action)
        except NoAlertPresentException:
            # Alert already dismissed because, user clicked OK to
            # signify that they have helped, as instructed above.
            return ActionResult.success(action)

    def _execute_by_key(self, run_context: RunContext, action: Action, key: str) -> ActionResult:
        if key.endswith('alert'):  # accept_alert|dismiss_alert
            result = self.__handle_alert(action)
        elif key == BrowserActionId.ASK_FOR_HELP.value:
            if run_context.get_arg(RunArg.BROWSER_TYPE, None) is None:
                raise ValueError(
                    "Cannot ask for help when browser is not visible. " 
                    "Set run option 'browser-mode' to 'visible' or 'undetected'.")
            result = self.ask_for_help(action)
        elif key == BrowserActionId.BROWSE_TO.value:
            result = self.__browse_to(action)
        elif key == BrowserActionId.DELETE_COOKIES.value:
            result = self.__delete_cookies(action)
        elif key == BrowserActionId.DISABLE_CURSOR.value:
            result = self.__disable_cursor(action)
        elif key == BrowserActionId.ENABLE_CURSOR.value:
            result = self.__enable_cursor(action)
        elif key == BrowserActionId.EXECUTE_SCRIPT.value:
            result = self.__execute_script(action)
        elif key == BrowserActionId.MOVE_BY_OFFSET.value:
            result = self.__move_by_offset(action)
        elif key == BrowserActionId.REFRESH.value:
            result = self.__refresh(action)
        elif key == BrowserActionId.SAVE_SCREENSHOT.value:
            result = self.__save_screenshot(action)
        elif key == BrowserActionId.SAVE_WEBPAGE.value:
            result = self.__save_webpage(action)
        else:
            return super()._execute_by_key(run_context, action, key)
        logger.debug(f'{result}')
        return result

    def __handle_alert(self, action: Action) -> ActionResult:
        how: str = action.get_name().split("_")[0]  # accept|dismiss
        value: str = action.get_first_arg_as_str()
        timeout = float(value) if value else self.__wait_timeout_seconds
        try:
            web_driver = self.get_web_driver()
            WebDriverWait(web_driver, timeout).until(wait_condition.alert_is_present())
            if how == 'accept':
                web_driver.switch_to.alert.accept()
            elif how == 'dismiss':
                web_driver.switch_to.alert.dismiss()
            else:
                raise ValueError(f"Unsupported: {action}")
        except TimeoutException:
            logger.debug(f"Timed out waiting for alert. {action}")

        return ActionResult(action, True)

    def __browse_to(self, action: Action) -> ActionResult:
        return ActionResult.success(action, self.__element_selector.load_page(action.get_arg_str()))

    def __delete_cookies(self, action: Action) -> ActionResult:
        file = get_cookies_file(action.get_agent_name())
        self.get_web_driver().delete_all_cookies()
        if os.path.exists(file):
            os.remove(file)
            logger.debug(f"Deleted cookies file: {file}")
        return ActionResult.success(action)

    def __disable_cursor(self, action: Action) -> ActionResult:
        # This is a hack.
        disable_cursor = """
                function disableCursor() {
                  var seleniumFollowerImg = document.getElementById('selenium_mouse_follower')
                  if (seleniumFollowerImg) {
                    document.body.removeChild(seleniumFollowerImg);
                  }
                };
        
                disableCursor();
        """
        result = self.get_web_driver().execute_script(disable_cursor)
        return ActionResult.success(action, result)

    def __enable_cursor(self, action: Action) -> ActionResult:
        # This is a hack.
        # See https://stackoverflow.com/questions/53900972/how-can-i-see-the-mouse-pointer-as-it-performs-actions-in-selenium
        enable_cursor = """
                function enableCursor() {
                  var seleniumFollowerImg = document.createElement("img");
                  seleniumFollowerImg.setAttribute('src', 'data:image/png;base64,'
                    + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
                    + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
                    + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
                    + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
                    + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
                    + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
                    + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
                    + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
                    + 'dAAAAABJRU5ErkJggg==');
                  seleniumFollowerImg.setAttribute('id', 'selenium_mouse_follower');
                  seleniumFollowerImg.setAttribute('style', 'position: absolute; z-index: 99999999999; pointer-events: none; left:0; top:0');
                  document.body.appendChild(seleniumFollowerImg);
                  document.addEventListener('mousemove', function (e) {
                    document.getElementById("selenium_mouse_follower").style.left = e.pageX + 'px';
                    document.getElementById("selenium_mouse_follower").style.top = e.pageY + 'px';
                  });  
                };
        
                enableCursor();
        """
        result = self.get_web_driver().execute_script(enable_cursor)
        return ActionResult.success(action, result)

    def __execute_script(self, action: Action) -> ActionResult:
        result = self.get_web_driver().execute_script(action.get_arg_str())
        return ActionResult.success(action, result)

    def __move_by_offset(self, action: Action) -> ActionResult:
        args = action.get_args()
        x: int = 0 if len(args) == 0 else args[0]
        y: int = 0 if len(args) < 2 else args[1]
        ActionChains(self.get_web_driver()).move_by_offset(x, y).perform()
        return ActionResult.success(action)

    def __refresh(self, action: Action) -> ActionResult:
        self.get_web_driver().refresh()
        return ActionResult.success(action)

    def __save_screenshot(self, action: Action) -> ActionResult:
        filepath = self.__get_results_file(action, '-screenshot.png')  # Must be png
        self.get_web_driver().save_screenshot(filepath)
        return ActionResult.success(action, filepath)

    def __save_webpage(self, action: Action) -> ActionResult:
        filepath = self.__get_results_file(action, '-webpage.html', True)
        write_content(self.get_web_driver().page_source, filepath)
        return ActionResult.success(action, filepath)

    @staticmethod
    def __get_results_file(action: Action, suffix: str, create_file_if_none: bool = False) -> str:
        file_path = (f'{action.get_agent_name()}.{action.get_stage_id()}'
                     f'.{action.get_stage_item_id()}{suffix}')
        file_path = get_cached_results_file(action.get_agent_name(), file_path)
        if create_file_if_none is True and not os.path.exists(file_path):
            create_file(file_path)
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return file_path

    @staticmethod
    def __wait_till_page_loaded(web_driver: WEB_DRIVER) -> None:
        try:
            WebDriverWait(web_driver, 10).until(
                wait_condition.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException as ex:
            logger.warning(f"Timed out waiting till page loaded: {ex}")

        time.sleep(5) # The above did not work in most cases, so we wait a bit more.


    def get_web_driver(self) -> WEB_DRIVER:
        return self.__element_selector.get_webdriver()

    def get_wait_timeout_seconds(self) -> float:
        return self.__wait_timeout_seconds

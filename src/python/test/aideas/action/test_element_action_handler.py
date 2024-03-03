import os

from selenium.webdriver.remote.webelement import WebElement

from ....main.aideas.action.action import Action
from ....main.aideas.action.action_result import ActionResult
from ....main.aideas.action.element_action_handler import ElementActionHandler
from ....main.aideas.env import Env


class TestElementActionHandler(ElementActionHandler):
    def __init__(self, webdriver, wait_timeout_seconds: float = 20):
        super().__init__(webdriver, wait_timeout_seconds)

    def with_timeout(self, timeout: float) -> 'ElementActionHandler':
        return TestElementActionHandler(self.get_web_driver(), timeout)

    def execute_on(self, action: Action, element: WebElement) -> ActionResult:
        # For tests, we don't implement element based actions.
        return self.execute(action)

    def execute(self, action: Action) -> ActionResult:
        if action.get_name() == TestElementActionHandler.ACTION_GET_NEWEST_FILE:
            file_type = os.environ[Env.VIDEO_OUTPUT_TYPE.value]
            return ActionResult(action, True, f'test-downloaded-video.{file_type}')
        return ActionResult(action, True, 'test-result')

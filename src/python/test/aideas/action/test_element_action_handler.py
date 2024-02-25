from selenium.webdriver.remote.webelement import WebElement

from ....main.aideas.action.action import Action
from ....main.aideas.action.action_result import ActionResult
from ....main.aideas.action.element_action_handler import ElementActionHandler


class TestElementActionHandler(ElementActionHandler):
    def __init__(self, webdriver, wait_timeout_seconds: float = 20):
        super().__init__(webdriver, wait_timeout_seconds)

    def with_timeout(self, timeout: float) -> 'ElementActionHandler':
        return TestElementActionHandler(self.get_web_driver(), timeout)

    def execute_on(self, action: Action, element: WebElement) -> ActionResult:
        return ActionResult(action, True, 'test-result')

    def execute(self, action: Action) -> ActionResult:
        return ActionResult(action, True, 'test-result')


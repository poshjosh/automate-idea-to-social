import os

from selenium.webdriver.remote.webelement import WebElement

from .....main.app.aideas.action.action import Action
from .....main.app.aideas.action.action_result import ActionResult
from .....main.app.aideas.action.action_handler import ActionId, BaseActionId
from .....main.app.aideas.action.element_action_handler import ElementActionHandler
from .....main.app.aideas.env import Env


class TestElementActionHandler(ElementActionHandler):
    def __init__(self, webdriver, wait_timeout_seconds: float = 20):
        super().__init__(webdriver, wait_timeout_seconds)

    def with_timeout(self, timeout: float) -> 'ElementActionHandler':
        return TestElementActionHandler(self.get_web_driver(), timeout)

    def execute_on(self, action: Action, element: WebElement) -> ActionResult:
        # For tests, we don't implement element based actions.
        result = self.execute(action)
        if action.is_negation():
            result = result.flip()
        return result

    def _execute(self, key: str, action: Action) -> ActionResult:
        if action == Action.none():
            return ActionResult.none()
        action_id: BaseActionId = ElementActionHandler.to_action_id(action.get_name_without_negation())
        result_producing: bool = action_id.is_result_producing()
        if key == ActionId.GET_NEWEST_FILE_IN_DIR.value:
            file_type = os.environ[Env.VIDEO_OUTPUT_TYPE.value]
            return ActionResult(action, True,
                                f'test-downloaded-video.{file_type}' if result_producing else None)
        return ActionResult(action, True,
                            'test-result' if result_producing else None)

import os

from aideas.app.action.action import Action
from aideas.app.action.action_result import ActionResult
from aideas.app.action.action_handler import ActionId, BaseActionId, TARGET
from aideas.app.action.element_action_handler import ElementActionHandler
from aideas.app.env import Env
from aideas.app.run_context import RunContext
from aideas.app.action.browser_action_handler import BrowserActionId


class TestElementActionHandler(ElementActionHandler):
    def execute_on(
            self, run_context: RunContext, action: Action, target: TARGET = None) -> ActionResult:
        # For tests, we don't implement element based actions.
        result = self.execute(run_context, action)
        if action.is_negation():
            result = result.flip()
        return result

    def _execute(self, run_context: RunContext, action: Action, key: str) -> ActionResult:
        if action == Action.none():
            return ActionResult.none()
        action_id: BaseActionId = ElementActionHandler.to_action_id(
            action.get_name_without_negation())
        result_producing: bool = action_id.is_result_producing()
        if key == ActionId.GET_NEWEST_FILE_IN_DIR.value:
            file_type = action.get_args_as_str_list()[1]
            return ActionResult(action, True,
                                f'test-downloaded-video.{file_type}' if result_producing else None)

        if (key == ActionId.LOG.value
                # or key == ActionId.EVAL.value
                # or key == ActionId.EXEC.value
                or key == ActionId.SET_CONTEXT_VALUES.value):
            return super()._execute(run_context, action, key)

        if (key == BrowserActionId.BROWSE_TO.value
                or key == BrowserActionId.DELETE_COOKIES.value
                or key == BrowserActionId.DISABLE_CURSOR.value
                or key == BrowserActionId.ENABLE_CURSOR.value
                or key == BrowserActionId.EXECUTE_SCRIPT.value
                or key == BrowserActionId.MOVE_BY_OFFSET.value
                or key == BrowserActionId.REFRESH.value):
            return super()._execute(run_context, action, key)

        return ActionResult(action, True,
                            'test-result' if result_producing else None)

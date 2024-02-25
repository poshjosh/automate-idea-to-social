import logging
import time

from .action import Action
from .action_result import ActionResult

logger = logging.getLogger(__name__)


class ActionHandler:
    def execute(self, action: Action) -> ActionResult:
        if action.get_name() == 'wait':
            result: ActionResult = self.wait(action)
            logger.debug(f"{result}")
            return result
        else:
            return ActionResult(action, False, f"Unsupported: {action}")

    def wait(self, action: Action) -> ActionResult:
        arg: str = action.get_first_arg()
        if arg is None or arg == '':
            return ActionResult(action, False, f"No value provided for: {action}")
        timeout: int = int(arg)
        if timeout < 1:
            return ActionResult(action, True)
        logger.debug(f"Waiting for {timeout} seconds")
        time.sleep(timeout)
        return ActionResult(action, True)

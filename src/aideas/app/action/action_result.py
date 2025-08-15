import logging
from .action import Action

logger = logging.getLogger(__name__)


class ActionResult:
    @staticmethod
    def none() -> 'ActionResult':
        return ActionResult.success(Action.none())

    @staticmethod
    def success(action: Action, result: any = None) -> 'ActionResult':
        return ActionResult(action, True, result)

    @staticmethod
    def failure(action: Action, result: any = None) -> 'ActionResult':
        return ActionResult(action, False, result)

    def __init__(self, action: Action, success: bool, result: any = None):
        self.__action = action
        self.__result = result
        self.__success = success

    def flip(self) -> 'ActionResult':
        logger.debug(f'Will flip result to: {not self.__success} from: {self.__success}')
        return ActionResult(self.__action, not self.__success, self.__result)

    def get_action(self) -> Action:
        return self.__action

    def get_result(self) -> any:
        return self.__result

    def is_success(self) -> any:
        return self.__success

    def __eq__(self, other) -> bool:
        return self.__action == other.__action and self.__result == other.__result \
            and self.__success == other.__success

    def __str__(self) -> str:
        return f'ActionResult(success={self.__success}, {self.__action}, result={self.__result})'
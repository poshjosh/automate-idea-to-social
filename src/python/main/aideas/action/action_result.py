from .action import Action


class ActionResult:
    @staticmethod
    def none() -> 'ActionResult':
        return NONE

    def __init__(self, action: Action, success: bool, result: any = None):
        self.__action = action
        self.__result = result
        self.__success = success

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


NONE = ActionResult(Action.none(), True)
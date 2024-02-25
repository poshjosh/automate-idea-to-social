import logging
from typing import Union

logger = logging.getLogger(__name__)


class Action:
    @staticmethod
    def none() -> 'Action':
        return NONE

    @staticmethod
    def of(target_id: str,
           action_signature: str,
           action_values: Union[dict[str, any], None] = None) -> 'Action':
        parts: list[str] = action_signature.split(' ')
        if len(parts) == 0:
            raise ValueError(f"Unsupported action: {target_id}.{action_signature}")
        name = parts[0]
        sval = '' if action_values is None \
            else action_values.get(name, {}).get(target_id, '')
        # If no action value is supplied as an argument to this method,
        # use the one split from the action signature.
        if sval is None or sval == '':
            if len(parts) > 1:
                args: list[str] = parts[1:]
            else:
                args: list[str] = []
        else:
            args: list[str] = sval.split(' ')

        return Action(target_id, name, args)

    def __init__(self, target_id: str, name: str, args: Union[list[str], None] = None):
        self.__target_id = target_id
        self.__name = name
        self.__args = [] if args is None else list(args)

    def get_target_id(self) -> str:
        return self.__target_id

    def get_name(self) -> str:
        return self.__name

    def get_first_arg(self, result_if_none: str = '') -> str:
        return len(self.__args) > 0 and self.__args[0] or result_if_none

    def get_args(self) -> list[str]:
        return self.__args

    def __eq__(self, other) -> bool:
        return self.__target_id == other.__target_id and self.__name == other.__name \
            and self.__args == other.__args

    def __str__(self) -> str:
        return f"Action({self.__target_id}.{self.__name}{self.__args})"


NONE: Action = Action('', '', [])

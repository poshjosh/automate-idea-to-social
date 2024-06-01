import logging
import os
import uuid
from typing import Union

from .variable_parser import get_run_arg_replacement
from ..config import tokenize
from ..env import get_agent_results_dir

logger = logging.getLogger(__name__)

NOT = 'not'


class Action:
    @staticmethod
    def none() -> 'Action':
        return NONE

    @staticmethod
    def of_generic(agent_name: str, stage_id: str, args: [str] = None) -> 'Action':
        return Action(
            agent_name,
            stage_id,
            f'{stage_id}-{uuid.uuid4().hex}',
            stage_id.replace('-', '_'),
            [] if args is None else args)

    @staticmethod
    def of(agent_name: str,
           stage_id: str,
           stage_item_id: str,
           action_signature: str,
           run_context: 'RunContext' = None) -> 'Action':
        if action_signature == 'none':
            return Action.none()
        parts: list[str] = tokenize(action_signature)
        if len(parts) == 0:
            raise ValueError(f'Unsupported action: {stage_item_id}.{action_signature}')

        name, args = Action.__split_into_name_and_args(parts)

        for i in range(len(args)):
            args[i] = get_run_arg_replacement(
                [agent_name, stage_id, stage_item_id], args[i], run_context)

        return Action(agent_name, stage_id, stage_item_id, name, args)

    def __init__(self,
                 agent_name: str,
                 stage_id: str,
                 stage_item_id: str,
                 name: str,
                 args: Union[list, None] = None):
        self.__agent_name = agent_name
        self.__stage_id = stage_id
        self.__stage_item_id = stage_item_id
        self.__name = name
        self.__args = [] if args is None else list(args)

    def get_results_dir(self) -> str:
        results_dir = get_agent_results_dir(self.__agent_name)
        return os.path.join(results_dir, self.get_stage_id(), self.get_stage_item_id())

    def get_agent_name(self) -> str:
        return self.__agent_name

    def get_stage_id(self) -> str:
        return self.__stage_id

    def get_stage_item_id(self) -> str:
        return self.__stage_item_id

    def get_name(self) -> str:
        return self.__name

    def is_negation(self) -> bool:
        return self.get_name().startswith(f'{NOT} ')

    def get_name_without_negation(self) -> str:
        name: str = self.get_name()
        return name.split(' ')[1] if self.is_negation() else name

    def require_first_arg_as_str(self) -> str:
        arg: any = self.get_first_arg()
        if not arg:
            raise ValueError(f'No argument provided for: {self}')
        return str(arg)

    def get_first_arg_as_str(self, default: any = None) -> str:
        arg: any = self.get_first_arg(default)
        return None if arg is None else str(arg)

    def get_first_arg(self, default: any = None) -> any:
        arg = None if len(self.__args) == 0 else self.__args[0]
        return default if arg is None else arg

    def get_args(self) -> list:
        return self.__args

    def get_arg_bool(self, default: bool = False) -> bool:
        arg: str = self.get_arg_str('')
        return default if arg == '' else arg == 'true'

    def get_arg_str(self, default: str = '') -> str:
        return default if not self.__args else ' '.join(self.get_args_as_str_list())

    def get_args_as_str_list(self) -> list[str]:
        return [str(e) for e in self.__args]

    @staticmethod
    def __split_into_name_and_args(parts: list[str]) -> tuple[str, [str]]:
        """
        Input: wait 3
        Output: (wait, [3])
        Input: not is_displayed
        Output: (not is_displayed, [])
        :param parts: The parts to split
        :return: The name and the arguments split from the parts
        """
        args_offset: int = 2 if parts[0] == NOT else 1
        name = ' '.join(parts[0:args_offset])
        args: [str] = parts[args_offset:] if len(parts) > args_offset else []
        return name, args

    def __eq__(self, other) -> bool:
        return (self.__agent_name == other.__agent_name and self.__stage_id == other.__stage_id
                and self.__stage_item_id == other.__stage_item_id and self.__name == other.__name
                and self.__args == other.__args)

    def __str__(self) -> str:
        return f'Action({self.__stage_item_id}.{self.__name}{self.__args})'


NONE: Action = Action('', '', '', '', [])

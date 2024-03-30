import logging
import os
import uuid
from typing import Union

from .variable_parser import parse_run_arg
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
           target_id: str,
           action_signature: str,
           run_context: 'RunContext' = None) -> 'Action':
        if action_signature == 'none':
            return Action.none()
        parts: list[str] = tokenize(action_signature)
        if len(parts) == 0:
            raise ValueError(f'Unsupported action: {target_id}.{action_signature}')

        name, args = Action.__split_into_name_and_args(parts)

        for i in range(len(args)):
            args[i] = parse_run_arg(
                [agent_name, stage_id, target_id], args[i], run_context)

        return Action(agent_name, stage_id, target_id, name, args)

    def __init__(self,
                 agent_name: str,
                 stage_id: str,
                 target_id: str,
                 name: str,
                 args: Union[list, None] = None):
        self.__agent_name = agent_name
        self.__stage_id = stage_id
        self.__target_id = target_id
        self.__name = name
        self.__args = [] if args is None else list(args)

    def get_results_dir(self) -> str:
        results_dir = get_agent_results_dir(self.__agent_name)
        return os.path.join(results_dir, self.get_stage_id(), self.get_target_id())

    def get_agent_name(self) -> str:
        return self.__agent_name

    def get_stage_id(self) -> str:
        return self.__stage_id

    def get_target_id(self) -> str:
        return self.__target_id

    def get_name(self) -> str:
        return self.__name

    def is_negation(self) -> bool:
        return self.get_name().startswith(f'{NOT} ')

    def get_name_without_negation(self) -> str:
        name: str = self.get_name()
        return name.split(' ')[1] if self.is_negation() else name

    def require_first_arg(self) -> str:
        arg: str = self.get_first_arg()
        if not arg:
            raise ValueError(f'No argument provided for: {self}')
        return arg

    def get_first_arg(self, default: any = None) -> any:
        arg = None if len(self.__args) == 0 else self.__args[0]
        return default if arg is None else arg

    def get_args(self) -> list:
        return self.__args

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
                and self.__target_id == other.__target_id and self.__name == other.__name
                and self.__args == other.__args)

    def __str__(self) -> str:
        return f'Action({self.__target_id}.{self.__name}{self.__args})'


NONE: Action = Action('', '', '', '', [])

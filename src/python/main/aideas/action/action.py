import logging
import os
import uuid
from typing import Union

from .variable_parser import parse_run_arg
from ..env import Env

logger = logging.getLogger(__name__)


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
        parts: list[str] = action_signature.split(' ')
        if len(parts) == 0:
            raise ValueError(f'Unsupported action: {target_id}.{action_signature}')

        name = parts[0]
        args: list = []

        if len(parts) > 1:
            args = parts[1:]
            for i in range(len(args)):
                args[i] = parse_run_arg(
                    [agent_name, stage_id, target_id], args[i], run_context)

        action = Action(agent_name, stage_id, target_id, name, args)
        action.__agents_dir = run_context.get_env(Env.AGENTS_DIR)
        return action

    def __init__(self,
                 agent_name: str,
                 stage_id: str,
                 target_id: str,
                 name: str,
                 args: Union[list, None] = None):
        self.__agents_dir = None
        self.__agent_name = agent_name
        self.__stage_id = stage_id
        self.__target_id = target_id
        self.__name = name
        self.__args = [] if args is None else list(args)

    def get_target_dir(self, agents_dir: Union[str, None] = None) -> str:
        agents_dir = self.__agents_dir if not agents_dir else agents_dir
        if not agents_dir:
            raise ValueError('agents dir required')
        return os.path.join(agents_dir, self.get_agent_name(),
                            self.get_stage_id(), self.get_target_id())

    def get_agent_name(self) -> str:
        return self.__agent_name

    def get_stage_id(self) -> str:
        return self.__stage_id

    def get_target_id(self) -> str:
        return self.__target_id

    def get_name(self) -> str:
        return self.__name

    def get_first_arg(self, result_if_none: any = None) -> any:
        return len(self.__args) > 0 and self.__args[0] or result_if_none

    def get_args(self) -> list:
        return self.__args

    def __eq__(self, other) -> bool:
        return (self.__agent_name == other.__agent_name and self.__stage_id == other.__stage_id
                and self.__target_id == other.__target_id and self.__name == other.__name
                and self.__args == other.__args)

    def __str__(self) -> str:
        return f'Action({self.__target_id}.{self.__name}{self.__args})'


NONE: Action = Action('', '', '', '', [])

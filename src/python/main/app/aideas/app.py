import pickle
import shutil
import uuid
from datetime import datetime
import logging
import os
import sys
from enum import Enum, unique
from typing import Union, Callable, TypeVar

from .agent.agent_factory import AgentFactory
from .env import Env, get_cached_results_dir, get_value
from .io.file import create_file
from .result.result_set import AgentResultSet, StageResultSet
from .config_loader import ConfigLoader
from .run_context import RunContext

logger = logging.getLogger(__name__)


class App:
    @staticmethod
    def of_defaults(source: Union[str, ConfigLoader]) -> 'App':
        if isinstance(source, str):
            config_loader = ConfigLoader(source)
        elif isinstance(source, ConfigLoader):
            config_loader = source
        else:
            raise ValueError(f"Source must be a string or a ConfigLoader, not {type(source)}")

        config = config_loader.load_app_config()
        agent_factory = AgentFactory(config_loader, config)
        return App(agent_factory, config)

    def __init__(self,
                 agent_factory: AgentFactory,
                 config: dict[str, any] = None):
        self.__agent_factory = agent_factory
        self.__config = config

    def run(self, agent_names: Union[str, list[str], None] = None) -> AgentResultSet:

        run_context: RunContext = RunContext.of_config(self.__config, agent_names)

        logger.debug(f"Running agents: {run_context.get_agent_names()}")

        for agent_name in run_context.get_agent_names():
            agent = self.__agent_factory.get_agent(agent_name)

            stage_result_set = agent.run(run_context)
            self.__save_agent_results(agent_name, stage_result_set)

        return run_context.get_result_set().close()

    def __save_agent_results(self, agent_name, result_set: StageResultSet):
        """
        Save the result to a file. (e.g. twitter/2021/01/01_12-34-56-uuid.pkl)
        Save a success file if the result is successful. (e.g. 01_12-34-56-uuid.pkl.success)
        :param agent_name: The name of the agent whose result is to be saved.
        :param result_set: The result to be saved.
        :return: None
        """
        now = datetime.now()
        object_path: str = os.path.join(get_cached_results_dir(agent_name),
                                        now.strftime("%Y"),
                                        now.strftime("%m"),
                                        f"{now.strftime('%d_%H-%M-%S')}-{uuid.uuid4().hex}.pkl")

        create_file(object_path)
        with open(object_path, 'wb') as file:
            pickle.dump(result_set, file)

        if result_set.is_successful():
            success_path = f'{object_path}.success'
            create_file(success_path)
        logger.debug(f"Agent: {agent_name}, result saved to: {object_path}")

        config_loader: ConfigLoader = self.__agent_factory.get_config_loader()
        config_path = config_loader.get_agent_config_path(agent_name)
        shutil.copy2(config_path, object_path.replace('.pkl', '.config.yaml'))


"""
The following code is used to parse command line arguments.
"""
T = TypeVar("T", bound=any)


@unique
class AppArg(str, Enum):
    def __new__(cls, value, env_name: Env = None):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__env_name = env_name
        return obj

    @property
    def alias(self) -> str:
        return self._value_

    @property
    def env_name(self) -> Union[Env, None]:
        return self.__env_name

    AGENTS = ('a', Env.AGENTS)


def get_list_arg_value(arg_name: AppArg) -> [str]:
    return __get_formatted_arg(arg_name, lambda x: x.split(','), [])


def __get_formatted_arg(arg: AppArg,
                        convert: Callable[[str], T],
                        result_if_none: Union[T, None] = None) -> T:
    arg_value = get_arg_value(arg, None)
    return result_if_none if arg_value is None else convert(arg_value)


def get_arg_value(arg: AppArg, result_if_none: Union[any, None] = None) -> any:
    """
    Get the value of the argument with the given name.
    Arguments have aliases that can be used to refer to them.
    --agents twitter could be written as -a twitter
    :param arg: The name of the argument.
    :param result_if_none: The result to return if none
    :return: The value of the argument with the given name.
    """
    args: [str] = [e.lower() for e in sys.argv]
    candidates: [str] = [f'--{arg.name.lower()}', f'-{arg.alias.lower()}']
    for candidate in candidates:
        if candidate in args:
            return args[args.index(candidate) + 1]
    return result_if_none if not arg.env_name else get_value(arg.env_name, result_if_none)

import logging.config
import os
import sys
from typing import Union, Callable, TypeVar

import yaml

from .agent.agent_factory import AgentFactory
from .result.agent_result_set import AgentResultSet
from .config_loader import ConfigLoader
from .run_context import RunContext

logger = logging.getLogger(__name__)


class App:
    @staticmethod
    def of_defaults(config_path: str,
                    logging_config_yaml: str = None,
                    app_config_yaml: str = None):
        config_loader = ConfigLoader(config_path)
        if logging_config_yaml is None:
            logging_config_yaml = config_loader.get_path_from_id('logging')

        App.init_logging(logging.config, logging_config_yaml)

        if app_config_yaml is None:
            config = config_loader.load_app_config()
        else:
            config = ConfigLoader.load_from_path(app_config_yaml)
        agent_factory = AgentFactory(config_loader, config)
        return App(agent_factory, config)

    @staticmethod
    def init_logging(logging_config, yaml_file_path):
        with open(yaml_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file.read())
            logging_config.dictConfig(config)
            logger.info(f'Done loading logging configuration from: {config_file}')

    def __init__(self,
                 agent_factory: AgentFactory,
                 config: dict[str, any] = None):
        self.__agent_factory = agent_factory
        self.__config = config

    def run(self, agent_names: Union[str, list[str], None] = None) -> AgentResultSet:

        run_context: RunContext = RunContext.of_config(self.__config, agent_names)

        for agent_name in run_context.get_agent_names():
            agent = self.__agent_factory.get_agent(agent_name)
            logger.debug(f"Starting agent: {agent_name}")

            agent.run(run_context)

            logger.debug(f"Agent: {agent_name}, "
                         f"result:\n{run_context.get_stage_results(agent_name)}")

        return run_context.get_result_set().close()


"""
The following code is used to parse command line arguments.
"""
ARG_AGENTS = "agents"

T = TypeVar("T", bound=any)

__arg_to_alias: dict[str, str] = {
    ARG_AGENTS: "a"
}


def get_list_arg(name: str) -> [str]:
    return __get_formatted_arg(name, lambda arg: arg.split(','), [])


def __get_formatted_arg(name: str,
                        convert: Callable[[str], T],
                        result_if_none: Union[T, None] = None) -> T:
    arg = get_arg(name, None)
    return result_if_none if arg is None else convert(arg)


def get_arg(name: str, result_if_none: Union[str, None] = None) -> any:
    """
    Get the value of the argument with the given name.
    Arguments have aliases that can be used to refer to them.
    --agents twitter could be written as -a twitter
    :param name: The name of the argument.
    :param result_if_none: The result to return if none
    :return: The value of the argument with the given name.
    """
    args: [str] = sys.argv
    if f'--{name}' in args:
        return args[args.index(f'--{name}') + 1]
    alias = __arg_to_alias.get(name)
    if alias is not None and f'-{alias}' in args:
        return args[args.index(f'-{alias}') + 1]
    env_value = os.environ.get(name)
    return env_value if env_value is not None else result_if_none

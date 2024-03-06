import logging.config
from typing import Union

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

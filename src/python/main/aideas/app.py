import logging.config
import yaml

from .agent.agent_factory import AgentFactory
from .agent.agent_inputs import AgentInputs
from .config_loader import ConfigLoader
from .action.action_result_set import ActionResultSet

logger = logging.getLogger(__name__)


class App:
    @staticmethod
    def of_defaults(logging_config_yaml: str = None,
                    app_config_yaml: str = None):
        agent_inputs = AgentInputs()
        if logging_config_yaml is None:
            logging_config_yaml = f'{ConfigLoader.get_config_path()}/logging.config.yaml'
        App.init_logging(logging.config, logging_config_yaml)

        if app_config_yaml is None:
            app_config_yaml = f'{ConfigLoader.get_config_path()}/app.config.yaml'
        config = ConfigLoader.load_from_path(app_config_yaml)
        agent_factory = AgentFactory(config)
        return App(agent_factory, agent_inputs, config)

    @staticmethod
    def init_logging(logging_config, yaml_file_path):
        with open(yaml_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file.read())
            logging_config.dictConfig(config)
            logger.info(f'Done loading logging configuration from: {config_file}')

    def __init__(self,
                 agent_factory: AgentFactory,
                 agent_inputs: AgentInputs,
                 config: dict[str, any]):
        self.__agent_factory = agent_factory
        self.__agent_inputs = agent_inputs
        self.__config = config

    def run(self) -> ActionResultSet:
        agent_names: list[str] = self.__config['agents']
        execution_result: ActionResultSet = ActionResultSet()
        try:
            for agent_name in agent_names:
                agent = self.__agent_factory.get_agent(agent_name)
                logger.debug(f"Starting agent: {agent_name}")
                curr_result: ActionResultSet = agent.run(self.__agent_inputs.get(agent_name))
                logger.debug(f"Result: {curr_result}, agent: {agent_name}")
                execution_result.add_all(curr_result)
        except Exception as ex:
            logger.exception(ex)
        return execution_result

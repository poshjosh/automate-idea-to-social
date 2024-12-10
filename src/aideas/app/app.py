import pickle
import shutil
import logging
from typing import Union

from .action.action import Action
from .action.action_result import ActionResult
from .agent.agent_factory import AgentFactory
from .env import get_cached_results_file
from .result.result_set import AgentResultSet, StageResultSet
from .config_loader import ConfigLoader
from .run_context import RunContext
from pyu.io.file import create_file

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

    @property
    def title(self):
        return self.__config["app"]["title"]

    def run(self, run_config: dict[str, any]) -> AgentResultSet:

        run_context: RunContext = RunContext.of_config(self.__config, run_config)
        continue_on_error = run_context.get_run_config().is_continue_on_error() is True

        agent_names = run_context.get_agent_names()

        logger.debug(f"Running agents: {agent_names}, continue_on_error: {continue_on_error}")

        for agent_name in agent_names:
            agent = self.__agent_factory.get_agent(agent_name)

            try:
                stage_result_set = agent.run(run_context)
                self.__save_agent_results(agent_name, stage_result_set)
            except Exception as ex:
                if continue_on_error:
                    logger.exception(ex)
                    result = run_context.get_stage_results(agent_name)
                    if not result or result.is_empty():
                        action = Action.of(agent_name, "*", "*", "*", run_context)
                        run_context.add_action_result(ActionResult.failure(action, "Error"))
                else:
                    raise ex
        return run_context.get_result_set().close()

    def __save_agent_results(self, agent_name, result_set: StageResultSet):
        """
        Save the result to a file. (e.g. twitter/2021/01/01_12-34-56-uuid.pkl)
        Save a success file if the result is successful. (e.g. 01_12-34-56-uuid.pkl.success)
        :param agent_name: The name of the agent whose result is to be saved.
        :param result_set: The result to be saved.
        :return: None
        """
        name: str = "result-set"
        object_path: str = get_cached_results_file(agent_name, f'{name}.pkl')

        create_file(object_path)
        with open(object_path, 'wb') as file:
            pickle.dump(result_set, file)

        if result_set.is_successful():
            success_path = f'{object_path}.success'
            create_file(success_path)
        logger.debug(f"Agent: {agent_name}, result saved to: {object_path}")

        config_loader: ConfigLoader = self.__agent_factory.get_config_loader()
        config_path = config_loader.get_agent_config_path(agent_name)
        shutil.copy2(config_path, f'{object_path[:object_path.index(name)]}config.yaml')
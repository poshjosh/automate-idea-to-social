import logging
import os.path
import shutil
from collections import OrderedDict

from ..config import AgentConfig, ConfigPath, Name
from ..env import get_agent_output_dir, get_agent_results_dir
from ..result.result_set import ElementResultSet, StageResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class AgentError(Exception):
    pass


class Agent:
    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: dict[str, 'Agent'] = None):
        self.__name = name
        self.__config = AgentConfig(agent_config)
        self.__dependencies = {} if dependencies is None else dependencies

    def with_config(self, config: dict[str, any]) -> 'Agent':
        clone: Agent = self.clone()
        clone.__config = AgentConfig(config)
        return clone

    def clone(self) -> 'Agent':
        return self.__class__(self.get_name(), self.get_config().root(), self._get_dependencies())

    def add_dependency(self, agent_name: str, agent: 'Agent') -> 'Agent':
        if agent is None:
            raise ValueError('Agent cannot be None')
        if agent_name != self.__name and agent_name in self.__dependencies.keys():
            raise ValueError(f'Agent {agent_name} is already a dependency of {self.__name}')
        self.__dependencies[agent_name] = agent
        return self

    def run(self, run_context: RunContext) -> StageResultSet:
        """Run all the stages of the agent and return True if successful, False otherwise."""
        logger.debug(f"Starting agent: {self.get_name()}")
        try:

            self.__clear_dirs()

            self.__config = AgentConfig(
                run_context.replace_variables(self.__name, self.__config.root()))

            stages: [Name] = self.__config.get_stage_names()

            # We only close the result for the agent after all stages have been run.
            return self._run_stages(run_context, stages).close()
        finally:
            try:
                self.close()
            except Exception as ex:
                logger.warning(f"Error closing agent: {self.__name}. {ex}")
            logger.debug(f"Agent: {self.get_name()}, "
                         f"results:\n{run_context.get_stage_results(self.get_name())}")

    def close(self):
        """Subclasses should implement this method as needed"""
        pass

    def _run_agent_stages(self,
                          run_context: RunContext,
                          agent_to_stages: OrderedDict[str, [Name]]):
        for agent_name in agent_to_stages.keys():
            agent: Agent = self if agent_name == self.__name else self.get_dependency(agent_name)
            stage_names: [Name] = agent_to_stages[agent_name]
            logger.debug(f"For {self.__name}, will run stages: {[str(e) for e in stage_names]}")

            agent._run_stages(run_context, stage_names)

    def _run_stages(self, run_context: RunContext, stages: [Name]) -> StageResultSet:
        """Run specified stages of the agent and return True if successful, False otherwise."""

        config: AgentConfig = self.get_config()

        for stage in stages:

            config_path: ConfigPath = ConfigPath.of(stage)
            index_var_key: str = config.get_iteration_index_variable(config_path)
            start: int = config.get_iteration_start(config_path)
            step: int = config.get_iteration_step(config_path)
            end: int = config.get_iteration_end(config_path)

            for index in range(start, end, step):
                # To avoid overriding previous results we qualify the stage id with the index
                # We do not qualify when the index is 0, to ensure the original stage id is used
                # Without iteration: stage_id
                #    With iteration: stage_id, stage_id1, stage_id2, ...stage_idN
                if index > 0:
                    stage = Name.of(stage.get_value(), f'{stage.get_id()}{index}')
                try:
                    run_context.set(index_var_key, index)
                    result = self.run_stage(run_context, stage)
                finally:
                    run_context.remove(index_var_key)
                logger.debug(f"Stage: {stage}, result: {result}")
                # We raise an exception if we want to stop the process
                # so no need to do this here.
                # if not result.is_successful():
                #     break

        # We do not close the result set here because a stage could be run within another stage
        # In that case, this point is not the end of the run stages process.
        # The closing is done at the run() method level
        return run_context.get_stage_results(self.__name)

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        """Run named stage of the agent and return True if successful, False otherwise."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_name(self) -> str:
        return self.__name

    def get_config(self) -> AgentConfig:
        return self.__config

    def _get_dependencies(self) -> dict[str, 'Agent']:
        return self.__dependencies

    def get_dependency(self, agent_name: str) -> 'Agent':
        return self.__dependencies[agent_name]

    def get_results_dir(self, agent_name: str = None):
        if not agent_name:
            agent_name = self.get_name()
        return get_agent_results_dir(agent_name)

    def get_output_dir(self, agent_name: str = None):
        if not agent_name:
            agent_name = self.get_name()
        return get_agent_output_dir(agent_name)

    def __clear_dirs(self):
        # Results dir is a sub-dir of the output dir
        if os.path.exists(self.get_output_dir()):
            shutil.rmtree(self.get_output_dir())
            logger.debug(f"Successfully removed dir: {self.get_output_dir()}")
        if not os.path.exists(self.get_results_dir()):
            os.makedirs(self.get_results_dir())
            logger.debug(f"Successfully created dir: {self.get_results_dir()}")

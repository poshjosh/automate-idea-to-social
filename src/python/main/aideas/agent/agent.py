import logging
from collections import OrderedDict

from ..config.name import Name
from ..result.element_result_set import ElementResultSet
from ..result.stage_result_set import StageResultSet
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
        self.__config = agent_config
        self.__dependencies = {} if dependencies is None else dependencies

    def add_dependency(self, agent_name: str, agent: 'Agent') -> 'Agent':
        if agent is None:
            raise ValueError('Agent cannot be None')
        if agent_name != self.__name and agent_name in self.__dependencies.keys():
            raise ValueError(f'Agent {agent_name} is already a dependency of {self.__name}')
        self.__dependencies[agent_name] = agent
        return self

    """Run all the stages of the agent and return True if successful, False otherwise."""

    def run(self, run_context: RunContext) -> StageResultSet:

        self.__config = run_context.replace_variables(self.__name, self.__config)

        stages: [Name] = Name.of_lists(list(self.get_stages_config().keys()))

        # We only close the result for the agent after all stages have been run.
        return self._run_stages(run_context, stages).close()

    def _run_agent_stages(self,
                          run_context: RunContext,
                          agent_to_stages: OrderedDict[str, [Name]]):
        for agent_name in agent_to_stages.keys():
            agent: Agent = self if agent_name == self.__name else self.get_dependency(agent_name)
            stage_names: [Name] = agent_to_stages[agent_name]
            logger.debug(f"For {self.__name}, will run: {agent_name}, stages: {stage_names}")

            agent._run_stages(run_context, stage_names)

    """Run specified stages of the agent and return True if successful, False otherwise."""

    def _run_stages(self, run_context: RunContext, stages: [Name]) -> StageResultSet:

        for stage in stages:

            result = self.run_stage(run_context, stage)
            logger.debug(f"Stage: {stage}, result: {result}")

            # We raise an exception if we want to stop the process
            # so no need to do this.
            # if not result_set.is_successful():
            #     break

        # We do not close the result set here because a stage could be run within another stage
        # In that case, this point is not the end of the run stages process.
        # The closing is done at the run() method level
        return run_context.get_stage_results(self.__name)

    """Run named stage of the agent and return True if successful, False otherwise."""

    def run_stage(self,
                  run_context: RunContext,
                  stage_name: Name) -> ElementResultSet:
        raise NotImplementedError("Subclasses must implement this method")

    def get_name(self) -> str:
        return self.__name

    def get_config(self) -> dict[str, any]:
        return self.__config

    def get_stages_config(self) -> dict[str, any]:
        return self.__config['stages']

    def get_stage_config(self, stage_name: str) -> dict[str, any]:
        return self.get_stages_config()[stage_name]

    def _get_dependencies(self) -> dict[str, 'Agent']:
        return self.__dependencies

    def get_dependency(self, agent_name: str) -> 'Agent':
        return self.__dependencies[agent_name]

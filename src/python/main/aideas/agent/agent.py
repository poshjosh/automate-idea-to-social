import logging
from typing import Union

from ..config.name import Name
from ..result.element_result_set import ElementResultSet
from ..result.stage_result_set import StageResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, name: str, agent_config: dict[str, any]):
        self.__name = name
        self.__config = agent_config

    """Run all the stages of the agent and return True if successful, False otherwise."""
    def run(self, run_context: RunContext) -> StageResultSet:
        stages_config: dict = self.__config['stages']
        return self.run_stages(run_context, list(stages_config.keys())).close()

    """Run specified stages of the agent and return True if successful, False otherwise."""
    def run_stages(self,
                   run_context: RunContext,
                   stage_names: list[str],
                   stage_ids: Union[list[str], None] = None) -> StageResultSet:
        if stage_ids is not None and len(stage_names) != len(stage_ids):
            raise ValueError("The number of stage names and aliases must be the same")
        stages_config: dict = self.__config['stages']

        # To be able to access elements by index, we cast to list
        stage_names: list[str] = list(stage_names)
        stage_ids: list[str] = list(stage_ids) if stage_ids is not None else None
        stage_count: int = len(stage_names)

        for i in range(stage_count):
            stage_name: str = stage_names[i]
            alias = stage_ids[i] if stage_ids is not None else stage_name
            result = self.run_stage(stages_config, Name.of(stage_name, alias), run_context).close()
            logger.debug(f"Stage: {alias}, result: {result}")

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
                  stages_config: dict[str, any],
                  stage_name: Name,
                  run_context: RunContext) -> ElementResultSet:
        raise NotImplementedError("Subclasses must implement this method")

    def get_name(self) -> str:
        return self.__name

    def get_config(self) -> dict[str, any]:
        return self.__config

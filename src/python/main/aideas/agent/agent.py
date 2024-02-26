import logging
from ..action.action_result_set import ActionResultSet

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, agent_config: dict[str, any]):
        self.__config = agent_config

    """Run all the stages of the agent and return True if successful, False otherwise."""
    def run(self, run_config: dict[str, any]) -> ActionResultSet:
        stages_config: dict = self.__config['stages']
        return self.run_stages(run_config, stages_config.keys())

    """Run specified stages of the agent and return True if successful, False otherwise."""
    def run_stages(self, run_config: dict[str, any], stage_names: [str]) -> ActionResultSet:
        stages_config: dict = self.__config['stages']
        result_set: ActionResultSet = ActionResultSet()
        for stage_name in stage_names:
            result = self.run_stage(stages_config, stage_name, run_config)
            logger.debug(f"Stage: {stage_name}, result: {result_set}")
            result_set.add_all(result)
            # We raise an exception if we want to stop the process
            # so no need to do this.
            # if result_set.is_successful() is False:
            #     break
        return result_set.close()

    """Run named stage of the agent and return True if successful, False otherwise."""
    def run_stage(self,
                  stages_config: dict[str, any],
                  stage_name: str,
                  run_config: dict[str, any]) -> ActionResultSet:
        """Subclasses should implement this method."""
        pass

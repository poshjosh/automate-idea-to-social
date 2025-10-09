from abc import ABC, abstractmethod

import logging
import os.path
import shutil
import time
from collections import OrderedDict

from ..action.action_handler import ActionError, ActionHandler
from ..agent.event_handler import EventHandler
from ..config import AgentConfig, ConfigPath, Name, ON_START
from ..env import get_agent_output_dir, get_agent_results_dir
from ..result.result_set import ElementResultSet, StageResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


INTERVAL_KEY = 'interval-seconds'


class ExecutionError(Exception):
    pass


class Agent(ABC):
    @classmethod
    def of_config(cls,
                  agent_name: str,
                  app_config: dict[str, any],
                  agent_config: dict[str, any],
                  dependencies: dict[str, 'Agent'] = None) -> 'Agent':
        interval_seconds: int = agent_config.get(INTERVAL_KEY, 0)
        action_handler = ActionHandler()
        event_handler = EventHandler(action_handler)
        return cls(agent_name, agent_config, dependencies, event_handler, interval_seconds)

    def __init__(self,
                 name: str,
                 agent_config: dict[str, any],
                 dependencies: dict[str, 'Agent'] = None,
                 event_handler: EventHandler = EventHandler(),
                 interval_seconds: int = 0):
        self.__name = name
        self.__config = AgentConfig(agent_config)
        self.__dependencies = {} if dependencies is None else dependencies
        self.__event_handler = event_handler
        self.__interval_seconds = interval_seconds

    @abstractmethod
    def _execute(self,
                 config: AgentConfig,
                 stage: Name,
                 run_context: RunContext) -> ElementResultSet:
        """
        Execute the agent logic for the given stage.
        raise ExecutionError in case of failure.
        """
        pass

    def close(self):
        """Close any resources held by the agent."""
        pass

    def without_events(self) -> 'Agent':
        clone: Agent = self.clone()
        clone.__event_handler = EventHandler.noop()
        return clone

    def with_config(self, config: dict[str, any]) -> 'Agent':
        clone: Agent = self.clone()
        clone.__config = AgentConfig(config)
        return clone

    def clone(self) -> 'Agent':
        return self.__class__(self.get_name(), self.get_config().to_dict(),
                              self._get_dependencies(),self.__event_handler, self.__interval_seconds)

    def add_dependency(self, agent_name: str, agent: 'Agent') -> 'Agent':
        if agent is None:
            raise ValueError('Agent cannot be None')
        if agent_name != self.__name and agent_name in self.__dependencies.keys():
            raise ValueError(f'Agent {agent_name} is already a dependency of {self.__name}')
        self.__dependencies[agent_name] = agent
        return self

    def create_dependency(self, name: str, config: dict[str, any]) -> 'Agent':
        return self.__class__(name, config, None, self.__event_handler, self.__interval_seconds)

    def run(self, run_context: RunContext) -> StageResultSet:
        """Run all the stages of the agent and return True if successful, False otherwise."""
        logger.debug(f"Starting agent: {self.get_name()}")
        try:

            self.__config = AgentConfig(
                run_context.replace_variables(self.__name, self.__config.to_dict()))

            if self.__config.is_clear_output_dir():
                self.__clear_dirs()

            self.__make_dirs()

            stages: list[Name] = self.__config.get_stage_names()

            # We only close the result for the agent after all stages have been run.
            return self._run_stages(run_context, stages).close()
        finally:
            try:
                self.close()
            except Exception as ex:
                logger.warning(f"Error closing agent: {self.__name}. {ex}")
            logger.debug(f"Agent: {self.get_name()}, "
                         f"result: {run_context.get_stage_results(self.get_name())}")

    def _run_agent_stages(self,
                          run_context: RunContext,
                          agent_to_stages: OrderedDict[str, [Name]]):
        for agent_name in agent_to_stages.keys():
            agent: Agent = self if agent_name == self.__name else self.get_dependency(agent_name)
            stage_names: list[Name] = agent_to_stages[agent_name]
            logger.debug(f"For {self.__name}, will run stages: {[str(e) for e in stage_names]}")

            agent._run_stages(run_context, stage_names)

    def _run_stages(self, run_context: RunContext, stages: list[Name]) -> StageResultSet:
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
                    stage = Name.of(stage.value, f'{stage.id}{index}')
                try:
                    run_context.set(index_var_key, index)
                    run_context.set('stage-name', stage.value)
                    run_context.set('stage-id', stage.id)
                    result = self.run_stage(run_context, stage)
                finally:
                    run_context.remove(index_var_key)
                    run_context.remove('stage-name')
                    run_context.remove('stage-id')
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
                  stage: Name) -> ElementResultSet:
        result = self.__run_stage(run_context, stage, 1)
        self.__sleep()
        return result

    def __run_stage(self,
                    run_context: RunContext,
                    stage: Name,
                    trials) -> ElementResultSet:

        config: AgentConfig = self.get_config()
        config_path: ConfigPath = ConfigPath.of(stage)

        logger.debug(f"Executing stage {config_path}")

        if config.get_actions(config_path):
            raise ValueError(f"actions are not supported at stage level. "
                             f"Current stage: {config_path}")

        def do_retry(_trials: int) -> ElementResultSet:
            logger.debug(f"Retrying {config_path}")
            return self.__run_stage(run_context, stage, _trials)

        exception = None
        result = ElementResultSet.none()
        try:

            to_proceed = self._stage_may_proceed(config, stage, run_context)

            if not to_proceed:
                return result

            self.__event_handler.handle_event(
                self.get_name(), config, config_path,
                ON_START, run_context, self._run_stages_without_events)

            result: ElementResultSet = self._execute(config, stage, run_context)

        except (ActionError, ExecutionError) as ex:
            logger.debug(f"Error acting on {config_path}\n{str(ex)}")
            exception = ex

        result = self.__event_handler.handle_result_event(
            self.get_name(), config, config_path, run_context,
            self._run_stages_without_events, do_retry, exception, result, trials)

        return ElementResultSet.none() if result is None else result

    def _stage_may_proceed(self,
                           config: AgentConfig,
                           stage: Name,
                           run_context: RunContext) -> bool:
        return True

    def _run_stages_without_events(
            self, context: RunContext, agent_to_stages: OrderedDict[str, [Name]]):
        logger.debug(f"Running stages {agent_to_stages}")
        # We don't want an infinite loop, so we run this event without events.
        self.without_events()._run_agent_stages(context, agent_to_stages)

    def __sleep(self):
        if self.__interval_seconds <= 0:
            return
        time.sleep(self.__interval_seconds)

    def get_name(self) -> str:
        return self.__name

    def get_config(self) -> AgentConfig:
        return self.__config

    def _get_dependencies(self) -> dict[str, 'Agent']:
        return self.__dependencies

    def get_dependency(self, agent_name: str) -> 'Agent':
        return self.__dependencies[agent_name]

    def get_event_handler(self) -> EventHandler:
        return self.__event_handler

    def get_interval_seconds(self) -> int:
        return self.__interval_seconds

    def get_results_dir(self, agent_name: str = None):
        if not agent_name:
            agent_name = self.get_name()
        return get_agent_results_dir(agent_name)

    def get_output_dir(self, agent_name: str = None):
        if not agent_name:
            agent_name = self.get_name()
        return get_agent_output_dir(agent_name)

    def __clear_dirs(self):
        if os.path.exists(self.get_output_dir()):
            shutil.rmtree(self.get_output_dir())
            logger.debug(f"Successfully removed dir: {self.get_output_dir()}")

    def __make_dirs(self):
        if not os.path.exists(self.get_results_dir()):
            os.makedirs(self.get_results_dir())
            logger.debug(f"Successfully created dir: {self.get_results_dir()}")

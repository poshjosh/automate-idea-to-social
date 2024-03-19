from collections import OrderedDict
import logging
from typing import Callable

from ..action.action import Action
from ..action.action_handler import ActionHandler
from ..action.action_signatures import parse_agent_to_stages
from ..agent.agent import AgentError
from ..config import AgentConfig, ConfigPath, Name, ON_ERROR, ON_SUCCESS
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)


class EventHandler:
    @staticmethod
    def noop() -> 'EventHandler':
        return NOOP

    def __init__(self, action_handler: ActionHandler):
        self.__action_handler: ActionHandler = action_handler

    def handle_event(self,
                     agent_name: str,
                     config: AgentConfig,
                     config_path: ConfigPath,
                     event_name: str,
                     run_context: RunContext,
                     run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None]) \
            -> ElementResultSet:
        return self.__handle_event(
            agent_name, config, config_path, event_name, run_context, run_stages, trials=1)

    def handle_result_event(self,
                            agent_name: str,
                            config: AgentConfig,
                            config_path: ConfigPath,
                            run_context: RunContext,
                            run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None],
                            retry: Callable[[int], ElementResultSet] = None,
                            exception: Exception = None,
                            result: ElementResultSet = None,
                            trials: int = 1) -> ElementResultSet:

        event_name = self.__determine_result_event_name(config, config_path, exception, result)

        return self.__handle_event(
            agent_name, config, config_path, event_name, run_context,
            run_stages, retry, exception, result, trials)

    def __handle_event(self,
                       agent_name: str,
                       config: AgentConfig,
                       config_path: ConfigPath,
                       event_name: str,
                       run_context: RunContext,
                       run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None],
                       retry: Callable[[int], ElementResultSet] = None,
                       exception: Exception = None,
                       result: ElementResultSet = None,
                       trials: int = 1) -> ElementResultSet:

        if event_name == ON_ERROR:
            logger.debug(f'For {config_path}, handling event: {event_name} '
                         f'with config: {config.get(config_path)}')

        action_signature_list = config.get_event_actions(config_path, event_name)

        stage_id = config_path.stage().get_id()
        target_id = config_path.name().get_id()

        index: int = -1
        for action_signature in action_signature_list:
            index += 1
            if action_signature == 'continue':
                if event_name == ON_ERROR:
                    logger.warning(
                        f'For {config_path}, will continue despite error: {type(exception)}!')
                    logger.exception(exception)
            elif action_signature == 'fail':
                raise AgentError(f'Error {config_path}, result: {result}') from exception
            elif action_signature.startswith('retry'):
                if trials < self.__max_trials(action_signature):
                    logger.debug(f'Retrying: {config_path}, tried {trials} already')
                    retry(trials + 1)
                else:
                    raise AgentError(
                        f'Max retries exceeded {config_path}, result: {result}') from exception
            elif action_signature.startswith('run_stages'):
                _, agent_to_stages = parse_agent_to_stages(
                    action_signature, agent_name, config_path.stage())
                run_stages(run_context, agent_to_stages)
            else:
                action = self.__create_action(
                    agent_name, stage_id, target_id, index,
                    event_name, action_signature, run_context)
                logger.debug(f"Executing event action: {action}")
                action_result = self.__action_handler.execute(action)
                run_context.add_action_result(agent_name, stage_id, action_result)

        return run_context.get_element_results(agent_name, stage_id)

    @staticmethod
    def __determine_result_event_name(config: AgentConfig,
                                      config_path: ConfigPath,
                                      exception: Exception,
                                      result_set: ElementResultSet) -> str:
        """
        Determine the event name to use based on the result set and the exception.
        :param config: The agent configuration
        :param config_path: The path to the aspect of the configuration which we are handling
        :param exception: The exception which was thrown during process, or None
        :param result_set: The result of the process, or None
        :return: The event name to use
        """
        if exception is not None or EventHandler.__has_failure(config, config_path, result_set):
            return ON_ERROR
        else:
            return ON_SUCCESS

    @staticmethod
    def __has_failure(config: AgentConfig,
                      config_path: ConfigPath,
                      result_set: ElementResultSet) -> bool:
        """
        Determine if the result set has a failure, excluding ignored stages and stage items.

        For stage items, it is sufficient to simply check if the result set is successful.
        On the other hand, for stages, we need to exclude ignored stage items.
        Ignored stage items, are those which have `onerror: continue`.

        If a stage-item fails:

        - succeeding stage-items will not be executed, unless
        `onerror` is set to `continue` for the stage-item.

        - the stage will fail, unless `onerror` is set to
        `continue` for the stage.

        :param config: The agent configuration
        :param config_path: The path to the aspect of the configuration which we are handling
        :param result_set: The result of the process, or None
        :return: true if the result set has a failure, false otherwise
        """
        if not result_set:
            # This happens if a condition to proceed with processing is not met
            # It does not indicate a failure, just that the condition for processing was not met.
            return False
        if config_path.is_stage_item():
            return not result_set.is_successful()
        elif config_path.is_stage():
            return EventHandler.__has_failure_excluding_ignored(config, config_path, result_set)
        else:
            raise ValueError(f'Expected path to stage or stage item, got: {config_path}')

    @staticmethod
    def __has_failure_excluding_ignored(config: AgentConfig,
                                        config_path: ConfigPath,
                                        result_set: ElementResultSet) -> bool:
        for target_id, result_list in result_set.items():
            target_cfg_path = config_path.join(target_id)
            if config.is_continue_on_event(target_cfg_path, ON_ERROR):
                continue
            for result in result_list:
                if not result.is_success():
                    return True
        return False

    @staticmethod
    def __create_action(agent_name: str,
                        stage_id: str,
                        target_id: str,
                        index: int,
                        event_name: str,
                        action_signature: str,
                        run_context: RunContext) -> Action:
        return Action.of(agent_name, stage_id, f"{target_id}[{index}]-{event_name}",
                         action_signature, run_context)

    @staticmethod
    def __max_trials(action_signature: str) -> int:
        max_retries: int = int(action_signature.split(' ')[1])
        return max_retries + 1


class NoopEventHandler(EventHandler):
    def __init__(self):
        super().__init__(ActionHandler.noop())

    def handle_event(self,
                     agent_name: str,
                     config: AgentConfig,
                     config_path: ConfigPath,
                     event_name: str,
                     run_context: RunContext,
                     run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None]) \
            -> ElementResultSet:
        return ElementResultSet.none()

    def handle_result_event(self,
                            agent_name: str,
                            config: AgentConfig,
                            config_path: ConfigPath,
                            run_context: RunContext,
                            run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None],
                            retry: Callable[[int], ElementResultSet] = None,
                            exception: Exception = None,
                            result: ElementResultSet = None,
                            trials: int = 1) -> ElementResultSet:
        return result


NOOP: EventHandler = NoopEventHandler()

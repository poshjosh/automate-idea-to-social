from collections import OrderedDict
import logging
from typing import Callable

from ..action.action import Action
from ..action.action_handler import ActionHandler
from ..action.action_signatures import event_action_signatures
from ..agent.agent import AgentError
from ..config import AgentConfig, Name
from ..result.result_set import ElementResultSet
from ..run_context import RunContext

logger = logging.getLogger(__name__)

ON_START = 'onstart'
ON_ERROR = 'onerror'
ON_SUCCESS = 'onsuccess'


class EventHandler:
    @staticmethod
    def noop() -> 'EventHandler':
        return NOOP

    def __init__(self, action_handler: ActionHandler):
        self.__action_handler: ActionHandler = action_handler

    def handle_event(self,
                     agent_name: str,
                     config: AgentConfig,
                     config_path: [str],
                     event_name: str,
                     run_context: RunContext,
                     run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None]) \
            -> ElementResultSet:
        return self.__handle_event(
            agent_name, config, config_path, event_name, run_context,
            run_stages, trials=1)

    def handle_result_event(self,
                            agent_name: str,
                            config: AgentConfig,
                            config_path: [str],
                            run_context: RunContext,
                            run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None],
                            retry: Callable[[int], ElementResultSet] = None,
                            exception: Exception = None,
                            result: ElementResultSet = None,
                            trials: int = 1) -> ElementResultSet:

        event_name = self.__determine_result_event_name(
            exception, result, config_path[-1], config.get(config_path))

        return self.__handle_event(
            agent_name, config, config_path, event_name, run_context,
            run_stages, retry, exception, result, trials)

    def __handle_event(self,
                       agent_name: str,
                       config: AgentConfig,
                       config_path: [str],
                       event_name: str,
                       run_context: RunContext,
                       run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None],
                       retry: Callable[[int], ElementResultSet] = None,
                       exception: Exception = None,
                       result: ElementResultSet = None,
                       trials: int = 1) -> ElementResultSet:

        action_signature_list = event_action_signatures(config.get(config_path), event_name)

        config_path_str = '.'.join(config_path)
        stage_id = config_path[1]
        key = config_path[-1]

        index: int = -1
        for action_signature in action_signature_list:
            index += 1
            if action_signature == 'continue':
                if event_name == ON_ERROR:
                    logger.warning(f'For {key}, will continue despite error!')
                return result
            elif action_signature == 'fail':
                raise AgentError(
                    f'Failed @{config_path_str}, result: {result}') from exception
            elif action_signature.startswith('retry'):
                if trials < self.__max_trials(action_signature):
                    logger.debug(f'Retrying: {key} after {event_name}, tried {trials} already')
                    return retry(trials + 1)
                else:
                    raise AgentError(
                        f'Max retries exceeded @{config_path_str}, result: {result}') from exception
            elif action_signature.startswith('run_stages'):
                args: [str] = action_signature.split(' ')[1:]
                agent_to_stages: OrderedDict[str, [Name]] = (
                    self.__parse_names(args, agent_name, stage_id))
                run_stages(run_context, agent_to_stages)
                return run_context.get_element_results(agent_name, stage_id)
            else:
                action = self.__create_action(
                    agent_name, stage_id, key, index, event_name, action_signature, run_context)
                logger.debug(f"Executing event action: {action}")
                action_result = self.__action_handler.execute(action)
                run_context.add_action_result(agent_name, stage_id, action_result)
                return run_context.get_element_results(agent_name, stage_id)

    @staticmethod
    def __determine_result_event_name(exception: Exception,
                                      result: ElementResultSet,
                                      key: str,
                                      event_config: dict[str, any]) -> str:
        if type(event_config) is not dict:
            event_config = {}

        if exception is not None or result is None or not result.is_successful():
            event_name = ON_ERROR
            logger.debug(f'For: {key}, handling event: {event_name} with config: {event_config}')
            return event_name
        else:
            return ON_SUCCESS

    @staticmethod
    def __parse_names(agent_stages: [str],
                      calling_agent: str, calling_stage: str) -> OrderedDict[str, list['Name']]:
        names: OrderedDict[str, list[Name]] = OrderedDict()
        # target format = `agent_name.stage_name` or simply `stage_name`  (agent_name is optional)
        for target in agent_stages:
            agent_name = calling_agent if '.' not in target else target.split('.')[0]
            stage_name = target if '.' not in target else target.split('.')[1]
            stage_alias = calling_stage  # if '.' not in target else target.split('.')[1]
            names[agent_name] = [Name.of(stage_name, stage_alias)]
        return names

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
    def __max_trials(action: str) -> int:
        max_retries: int = int(action.split(' ')[1])
        return max_retries + 1


class NoopEventHandler(EventHandler):
    def __init__(self):
        super().__init__(ActionHandler.noop())

    def handle_event(self,
                     agent_name: str,
                     config: AgentConfig,
                     config_path: [str],
                     event_name: str,
                     run_context: RunContext,
                     run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None]) \
            -> ElementResultSet:
        return ElementResultSet.none()

    def handle_result_event(self,
                            agent_name: str,
                            config: AgentConfig,
                            config_path: [str],
                            run_context: RunContext,
                            run_stages: Callable[[RunContext, OrderedDict[str, [Name]]], None],
                            retry: Callable[[int], ElementResultSet] = None,
                            exception: Exception = None,
                            result: ElementResultSet = None,
                            trials: int = 1) -> ElementResultSet:
        return result


NOOP: EventHandler = NoopEventHandler()

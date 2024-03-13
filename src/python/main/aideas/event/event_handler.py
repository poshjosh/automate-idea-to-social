from collections import OrderedDict
import logging
from typing import Callable

from ..action.action import Action
from ..action.action_handler import ActionHandler
from ..action.action_signatures import event_action_signatures
from ..agent.agent import AgentError
from ..config import AgentConfig, ConfigPath, Name
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

        event_name = self.__determine_result_event_name(exception, result)

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

        action_signature_list = event_action_signatures(config.get(config_path), event_name)

        stage_id = config_path.stage().get_id()
        target_id = config_path.name().get_id()

        index: int = -1
        for action_signature in action_signature_list:
            index += 1
            if action_signature == 'continue':
                if event_name == ON_ERROR:
                    logger.warning(f'For {config_path}, will continue despite error!')
            elif action_signature == 'fail':
                raise AgentError(f'Error {config_path}, result: {result}') from exception
            elif action_signature.startswith('retry'):
                if trials < self.__max_trials(action_signature):
                    logger.debug(f'Retrying: {config_path} after {event_name}, '
                                 f'tried {trials} already')
                    retry(trials + 1)
                else:
                    raise AgentError(
                        f'Max retries exceeded {config_path}, result: {result}') from exception
            elif action_signature.startswith('run_stages'):
                args: [str] = action_signature.split(' ')[1:]
                agent_to_stages: OrderedDict[str, [Name]] = (
                    self.__parse_names(args, agent_name, config_path.stage()))
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
    def __determine_result_event_name(exception: Exception,
                                      result: ElementResultSet) -> str:
        if exception is not None or result is None or not result.is_successful():
            return ON_ERROR
        else:
            return ON_SUCCESS

    @staticmethod
    def __parse_names(agent_stages: [str],
                      calling_agent: str, calling_stage: Name) -> OrderedDict[str, list['Name']]:
        names: OrderedDict[str, list[Name]] = OrderedDict()
        # target format = `agent_name.stage_name` or simply `stage_name`  (agent_name is optional)
        for target in agent_stages:
            agent_name = calling_agent if '.' not in target else target.split('.')[0]
            stage_name = target if '.' not in target else target.split('.')[1]
            stage_alias = calling_stage.get_id()  # if '.' not in target else target.split('.')[1]
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

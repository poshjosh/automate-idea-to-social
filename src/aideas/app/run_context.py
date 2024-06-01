from enum import Enum
from typing import Union

from .action.action_result import ActionResult
from .action.variable_parser import replace_all_variables
from .env import Env
from .result.result_set import AgentResultSet, ElementResultSet, StageResultSet


CURRENT_URL = 'current_url'
CURRENT_ELEMENT = 'current_element'


class RunContext:
    @staticmethod
    def none() -> 'RunContext':
        return NONE

    @staticmethod
    def of_config(app_config: dict[str, any],
                  agent_names: Union[str, list[str], None] = None) -> 'RunContext':
        app_name = app_config['app']['name']
        return RunContext(app_config, agent_names, Env.load(app_name))

    def __init__(self,
                 app_config: dict[str, any],
                 agent_names: Union[str, list[str], None] = None,
                 args: dict[str, any] = None):
        self.__agent_names: list[str] = self.__to_list(app_config, agent_names)
        self.__args: dict[str, any] = args
        self.__result_set: AgentResultSet = AgentResultSet()
        self.__values = {}

    def replace_variables(self, agent_name: str, config: dict[str, any]) -> dict[str, any]:
        config = replace_all_variables(config, self.__args)
        self.__values[agent_name] = config
        return config

    def add_action_result(self,
                          agent_name: str,
                          stage_id: str,
                          result: ActionResult) -> 'RunContext':
        new_stage = False
        new_stage_element = False
        stage_result_set: StageResultSet = self.get_stage_results(agent_name, None)
        if stage_result_set is None:
            new_stage = True
            stage_result_set = StageResultSet()
        element_result_set: ElementResultSet = stage_result_set.get(stage_id, None)
        if element_result_set is None:
            new_stage_element = True
            element_result_set = ElementResultSet()
        element_result_set.add(result)
        if new_stage_element:
            stage_result_set.set(stage_id, element_result_set)
        if new_stage:
            self.__result_set.set(agent_name, stage_result_set)
        return self

    def get_action_results(self,
                           agent_name: str,
                           stage_id: str,
                           element_name: str) -> list[ActionResult]:
        element_result_set: ElementResultSet = self.get_element_results(agent_name, stage_id)
        return [] if element_result_set is None else element_result_set.get(element_name, [])

    def get_action_result(self,
                          agent_name: str,
                          stage_id: str,
                          result_if_none: Union[ActionResult, None] = ActionResult.none()) \
            -> ActionResult:
        result_set: ElementResultSet = self.get_element_results(agent_name, stage_id)
        if result_set.is_empty():
            return result_if_none
        key: str = next(iter(result_set.keys()))
        action_result_list: list[ActionResult] = result_set.get(key, [])
        action_result = None if len(action_result_list) == 0 else action_result_list[0]
        return action_result if action_result is not None else result_if_none

    def get_element_results(self,
                            agent_name: str,
                            stage_id: str,
                            result_if_no: Union[ElementResultSet, None] = ElementResultSet.none()) \
            -> ElementResultSet:
        stage_result_set: StageResultSet = self.get_stage_results(agent_name)
        return result_if_no if stage_result_set is None else (
            stage_result_set.get(stage_id, result_if_no))

    def get_stage_results(self,
                          agent_name: str,
                          result_if_none: Union[StageResultSet, None] = StageResultSet.none()) \
            -> StageResultSet:
        return self.__result_set.get(agent_name, result_if_none)

    def get_agent_names(self) -> list[str]:
        return [e for e in self.__agent_names]

    def get_env(self, key: Enum, result_if_none: Union[any, None] = None) -> any:
        return self.get_arg(key.value, result_if_none)

    def get_arg(self, key: str, result_if_none: Union[any, None] = None) -> any:
        return self.__args.get(key, result_if_none)

    def get(self, key: str, result_if_none: Union[any, None] = None) -> any:
        return self.__values.get(key, result_if_none)

    def get_current_url(self, result_if_none: str = None) -> str:
        return self.get(CURRENT_URL, result_if_none)

    def set(self, key: str, value: any) -> Union[any or None]:
        result = self.get(key)
        self.__values[key] = value
        return result

    def remove(self, key: str) -> Union[any or None]:
        return self.__values.pop(key, None)

    def set_current_url(self, value: str) -> 'RunContext':
        self.__values[CURRENT_URL] = value
        return self

    def get_current_element(self, result_if_none: any = None) -> any:
        return self.get(CURRENT_ELEMENT, result_if_none)

    def set_current_element(self, value: any) -> 'RunContext':
        self.__values[CURRENT_ELEMENT] = value
        return self

    def get_result_set(self) -> AgentResultSet:
        return self.__result_set

    @staticmethod
    def __to_list(config: dict[str, any],
                  agent_names: Union[str, list[str], None] = None) -> list[str]:
        if agent_names is None or agent_names == '':
            return config.get('agents', [])
        elif isinstance(agent_names, list):
            return config.get('agents', []) if len(agent_names) == 0 else agent_names
        else:
            return config.get('agents', []) if len(agent_names) == 0 else [str(agent_names)]


NONE = RunContext({}, [], {})

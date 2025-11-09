import logging

from enum import Enum
from typing import Union, Any

from .action.action_result import ActionResult
from .action.variable_parser import replace_all_variables
from .config import AppConfig, RunConfig, RunArg
from .env import Env, get_app_language as env_get_app_language
from .i18n import DEFAULT_LANGUAGE_CODE
from .result.result_set import AgentResultSet, StageResultSet, ElementResultSet

logger = logging.getLogger(__name__)

CURRENT_URL = 'current_url'
CURRENT_ELEMENT = 'current_element'


class RunContext:
    @staticmethod
    def none() -> 'RunContext':
        return RunContext({}, {})

    @staticmethod
    def of_config(app_config: dict[str,  Any],
                  run_config: dict[str,  Any]) -> 'RunContext':
        app_name = app_config['app']['name']

        run_opts = {'app.name': app_name}

        Env.collect(run_opts)

        run_opts.update(run_config)

        return RunContext(app_config, run_opts)

    def __init__(self,
                 app_config: dict[str,  Any],
                 run_config: dict[str,  Any]):
        self.__app_config = AppConfig(app_config)
        self.__run_config = RunConfig(run_config)
        self.__agent_names = self.__run_config.get_agents()
        self.__args: dict[str,  Any] = run_config
        self.__args_formatted = {}
        for k, v in self.__args.items():
            self.__args_formatted[RunContext._format_key(k)] = v
        self.__result_set: AgentResultSet = AgentResultSet()
        self.__values = {}

    # TODO - Make blog agent an action and then remove this
    def get_language_codes_str(self) -> str:
        str_or_array = self.get_arg(RunArg.LANGUAGE_CODES, None)
        if str_or_array:
            return str_or_array if isinstance(str_or_array, str) else ','.join(str_or_array)
        else:
            return self.get_env(Env.TRANSLATION_OUTPUT_LANGUAGE_CODES, "")

    def replace_variables(self, agent_name: str, config: dict[str,  Any]) -> dict[str,  Any]:
        config = replace_all_variables(config, self.__args)
        self.__values[agent_name] = config
        return config

    def add_action_result(self, result: ActionResult) -> 'RunContext':
        self.__result_set.add_action_result(result)
        return self

    def get_element_results(self,
                            agent_name: str,
                            stage_id: str,
                            result_if_no: Union[ElementResultSet, None] = ElementResultSet.none()) \
            -> ElementResultSet:
        return self.__result_set.get_element_results(agent_name, stage_id, result_if_no)

    def get_stage_results(self,
                          agent_name: str,
                          result_if_none: Union[StageResultSet, None] = StageResultSet.none()) \
            -> StageResultSet:
        return self.__result_set.get_stage_results(agent_name, result_if_none)

    def get_agent_names(self) -> list[str]:
        return list(self.__agent_names)

    def get_app_language(self) -> str:
        return self.get_arg(RunArg.INPUT_LANGUAGE_CODE, env_get_app_language(True, self.__app_config.get_app_language(DEFAULT_LANGUAGE_CODE)))

    @staticmethod
    def _format_key(key: str):
        return key if not key else key.replace('_', '').replace('-', '').lower()

    def values(self, keys: list[Union[str, Enum]]) -> dict[str,  Any]:
        result = {}
        run_config = self.__run_config.to_dict()
        for key in keys:
            key_str: str = str(key.value) if isinstance(key, Enum) else str(key)
            result[key_str] = self._value(key, run_config.get(key_str, None))
        return result

    def value(self, key: Union[str, Enum], result_if_none: Union[Any, None] = None) ->  Any:
        run_config = self.__run_config.to_dict()
        key_str: str = str(key.value) if isinstance(key, Enum) else str(key)
        return self.get_arg(key, self.get(key_str, run_config.get(key_str, result_if_none)))

    def _value(self, key: Union[str, Enum], result_if_none: Union[Any, None] = None) ->  Any:
        key_str: str = str(key.value) if isinstance(key, Enum) else str(key)
        return self.get_arg(key, self.get(key_str, result_if_none))

    def get_env(self, key: Enum, result_if_none: Union[Any, None] = None) ->  Any:
        return self.get_arg(key, result_if_none)

    def get_arg(self, key: Union[str, Enum], result_if_none: Union[Any, None] = None) ->  Any:
        key_str: str = str(key.value) if isinstance(key, Enum) else str(key)
        return self.__args_formatted.get(RunContext._format_key(key_str), result_if_none)

    def get(self, key: str, result_if_none: Union[Any, None] = None) ->  Any:
        return self.__values.get(key, result_if_none)

    def get_current_url(self, result_if_none: str = None) -> str:
        return self.get(CURRENT_URL, result_if_none)

    def set(self, key: str, value:  Any) -> Union[Any, None]:
        result = self.get(key)
        self.__values[key] = value
        return result

    def remove(self, key: str) -> Union[Any, None]:
        return self.__values.pop(key, None)

    def set_current_url(self, value: str) -> 'RunContext':
        self.__values[CURRENT_URL] = value
        return self

    def get_current_element(self, result_if_none:  Any = None) ->  Any:
        return self.get(CURRENT_ELEMENT, result_if_none)

    def set_current_element(self, value:  Any) -> 'RunContext':
        self.__values[CURRENT_ELEMENT] = value
        return self

    def get_result_set(self) -> AgentResultSet:
        return self.__result_set

    def get_app_config(self) -> AppConfig:
        return self.__app_config

    def get_run_config(self) -> RunConfig:
        return self.__run_config
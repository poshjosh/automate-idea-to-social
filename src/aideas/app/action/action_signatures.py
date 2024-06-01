from collections import OrderedDict
from typing import TypeVar, Union

from ..config import AgentConfig, ACTIONS_KEY, DEFAULT_ACTIONS_KEY, Name, check_for_typo

STR_OR_DICT = TypeVar("STR_OR_DICT", bound=Union[str, dict])
STR_OR_LIST = TypeVar("STR_OR_LIST", bound=Union[str, list[str]])

DEFAULT_ACTIONS: list[str] = ['click']


# TODO - Move this function to config.py
def element_action_signatures(config: dict[str, any], element_name: str) -> list[str]:
    if AgentConfig.is_default_actions_key(element_name):
        raise ValueError(f'The provided key (i.e {element_name}) is a reserved word.')
    default_actions: list[str] = __element_action_signatures(
        config, DEFAULT_ACTIONS_KEY, DEFAULT_ACTIONS)
    element_config: STR_OR_DICT = config[element_name]
    if isinstance(element_config, str):
        return default_actions if len(default_actions) > 0 else DEFAULT_ACTIONS
    elif isinstance(element_config, dict):
        return __element_action_signatures(element_config, ACTIONS_KEY, default_actions)
    else:
        raise ValueError(f'Unexpected element config type: {type(element_config)}')


def __element_action_signatures(config: dict[str, any],
                                name: str,
                                result_if_none: list[str]) -> list[str]:
    check_for_typo(config, name)
    default_actions: STR_OR_LIST = result_if_none if not config \
        else config.get(name, result_if_none)
    return __to_list(default_actions)


def __to_list(source: Union[str, list]) -> list[str]:
    if isinstance(source, str):
        return [source]
    elif isinstance(source, list):
        return source
    else:
        raise ValueError(f'Invalid type for: {source}, expected list | str')


def parse_agent_to_stages(action_signature: [str],
                          calling_agent: str,
                          calling_stage: Union[str, Name]) \
        -> tuple[str, OrderedDict[str, list[Name]]]:
    calling_stage = Name.of(calling_stage)
    parts = action_signature.split(' ')
    action_name: str = parts[0]
    agent_stages: [str] = parts[1:]
    agent_to_stages: OrderedDict[str, list[Name]] = OrderedDict()
    # target format = `agent_name.stage_name` or simply `stage_name`  (agent_name is optional)
    for target in agent_stages:
        agent_name = calling_agent if '.' not in target else target.split('.')[0]
        stage_name = target if '.' not in target else target.split('.')[1]
        stage_alias = calling_stage.id  # if '.' not in target else target.split('.')[1]
        stage = Name.of(stage_name, stage_alias)
        stages = agent_to_stages.get(agent_name, [])
        stages.append(stage)
        agent_to_stages[agent_name] = stages
    return action_name, agent_to_stages

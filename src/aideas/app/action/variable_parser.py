import logging
import os
from typing import Union, Callable

from pyu.io.variable_parser import contains_variable, get_scoped_value, \
    get_scoped_value_for_name_having_prefix, replace_all_variables as replace_all, \
    replace_variables, VARIABLE_ANCHOR

from ..config import STAGES_KEY, STAGE_ITEMS_KEY

"""
Each run may involve one or more agents. All the agents involved 
share the same RunContext. Each agent has its own configuration.
From the agent configuration file (e.g yaml), access is provided
to each of the following:

context: This is the run context. Variables are resolved on the fly.
Example: `${context.context-available-attribute}`

results: This is the available results. Variables are resolved on the fly.
Example format: `${results.agent.stage.stage-item[ACTION_INDEX]}`

self: This is the agent's configuration. Variables are resolved prior to the run.
Example format: `${self.configuration-defined-attribute}`
"""
RESULTS_KEY = 'results'
CONTEXT_KEY = 'context'

NODES_TO_SKIP = [STAGES_KEY, STAGE_ITEMS_KEY]

logger = logging.getLogger(__name__)


def contains_action_variable(value: any) -> bool:
    if not isinstance(value, str):
        return False
    """Action variables are only available while the actions are being run"""
    return (__contains_variable_with_prefix(value, RESULTS_KEY)
            or __contains_variable_with_prefix(value, CONTEXT_KEY))


def __contains_variable_with_prefix(value: str, prefix: str) -> bool:
    if f'{VARIABLE_ANCHOR}{prefix}' in value:
        return True
    s = VARIABLE_ANCHOR + '{' + prefix
    if s in value:
        return True if '}' in value[value.index(s) + len(s):] else False
    return False


def replace_all_variables(
        target: dict[str, any],
        source: Union[dict[str, any], None] = None,
        check_replaced: bool = True) -> dict[str, any]:
    if not source:
        source = dict(os.environ)

    def check_variables_replaced(text: str) -> str:
        if not check_replaced:
            return text
        if contains_variable(text) and not contains_action_variable(text):
            raise ValueError(f'Failed to replace variables in: {text}')
        return text

    return replace_all(target, source, check_variables_replaced, NODES_TO_SKIP)


def get_run_arg_replacement(curr_path: list[str], arg: str, run_context: 'RunContext' = None) -> any:
    if len(curr_path) != 3:
        raise ValueError(f'Expected 3 elements, found: {curr_path}')

    def replace(name: str) -> any:
        return __get_run_arg_replacement(curr_path, name, run_context, None)

    replacement = replace_variables(arg, replace)

    if replacement is None:
        raise ValueError(f'Unsupported argument: {arg}, @ {".".join(curr_path)}')

    if contains_variable(replacement):
        raise ValueError(
            f'Invalid replacement: {replacement} for: {arg}, @ {".".join(curr_path)}')

    return replacement


def get_variables(config: dict[str, any], include_scoped_variables: bool = True) -> list[str]:

    variables = []

    def is_scoped_variable(variable: str) -> bool:
        return '.' in variable

    def accept(variable: str) -> bool:
        return include_scoped_variables or is_scoped_variable(variable) is False

    def collect_variable(variable) -> str:
        if accept(variable):
            variables.append(variable)
        return variable

    def visit(text: str, _: [str]) -> str:
        replace_variables(text, collect_variable)
        return text

    __visit_all_variables(config, visit)
    #
    # logger.info(f"\nFound variables: {variables}\nIn config:\n{config}")

    return variables


def __get_run_arg_replacement(curr_path: list[str],
                              name: str,
                              run_context: 'RunContext' = None,
                              result_if_none: Union[str, None] = None) -> Union[any, None]:
    replacement = None if run_context is None else run_context.get_arg(name)

    if replacement is None:

        def get(key: str):
            return None if run_context is None else run_context.get(key)

        replacement = get_scoped_value_for_name_having_prefix(
            curr_path, name, CONTEXT_KEY, get, NODES_TO_SKIP)

        if replacement is None:
            replacement = __get_results_value(curr_path, name, run_context)

    return result_if_none if replacement is None else replacement


def __get_results_value(curr_path: [str],
                        name: str,
                        run_context: 'RunContext' = None) -> Union[any, None]:
    def get_value(scope: any, key: str) -> any:
        if scope is None:
            return None if run_context is None else run_context.get_stage_results(key, None)
        else:
            return scope.get(key, None)

    value = get_scoped_value(curr_path, name, RESULTS_KEY, get_value, NODES_TO_SKIP)
    return __get_result(value)


def __get_result(value):
    if value is None:
        return None
    try:
        if isinstance(value, list):
            return [e.get_result() for e in value]
        return value.get_result()
    except Exception:
        return value


def to_variable(paths: [str]) -> str:
    return __to_variable(paths)


def to_results_variable(paths: [str]) -> str:
    paths = paths[0:]  # We use a copy of the list argument
    paths.insert(0, RESULTS_KEY)
    return __to_variable(paths)


def __to_variable(paths: [str], prefix: str = VARIABLE_ANCHOR, suffix: str = '') -> str:
    result = None
    for name in paths:
        if result is None:
            result = prefix + name
        else:
            result += f'.{name}'
    return result + suffix


# TODO - Make this method public in pyu.io.variable_parser and use the public method here
def __visit_all_variables(target: dict[str, any],
                          visit: Callable[[str, [str]], str],
                          path: [str] = None):
    def iter_dict(d: dict[str, any], _, curr_path: [str]):
        for k, v in d.items():
            d[k] = iter_value(v, d, curr_path)
        return d

    def iter_list(e_list: list[any], _, curr_path: [str]):
        for i, e in enumerate(e_list):
            e_list[i] = iter_value(e, e_list, curr_path)
        return e_list

    def iter_value(e: any, parent: any, curr_path: [str]):
        if isinstance(e, dict):
            return iter_dict(e, parent, curr_path)
        elif isinstance(e, list):
            return iter_list(e, parent, curr_path)
        elif isinstance(e, str):
            return visit(e, curr_path)
        else:
            return e

    iter_dict(target, None, [] if path is None else path)

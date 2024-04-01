import copy
import logging
from typing import Union, Tuple, Callable

from ..env import Env

"""
Each run may involve one or more agents. All the agents involved 
share the same RunContext. Each agent has its own configuration.
From the agent configuration file (e.g yaml), access is provided
to each of the following:

context: This is the run context. Variables are resolve at run time.
Example: `${context.context-available-attribute}`

results: This is the available results. Variables are resolved at run time.
Example format: `${results.agent.stage.stage-item[ACTION_INDEX]}`

self: This is the agent's configuration. Variables are resolved prior to the run.
Example format: `${self.configuration-defined-attribute}`
"""
RESULTS_KEY = 'results'
CONTEXT_KEY = 'context'
SELF_KEY = 'self'
VARIABLE_ANCHOR = '$'

logger = logging.getLogger(__name__)


def is_variable(value: str) -> bool:
    if VARIABLE_ANCHOR in value:
        return True
    s = VARIABLE_ANCHOR + '{'
    if s in value:
        return True if '}' in value[value.index(s) + len(s):] else False
    return False


def is_action_variable(value: str) -> bool:
    """Action variables are only available while the actions are being run"""
    return (__is_variable_with_prefix(value, RESULTS_KEY)
            or __is_variable_with_prefix(value, CONTEXT_KEY))


def __is_variable_with_prefix(value: str, prefix: str) -> bool:
    if f'{VARIABLE_ANCHOR}{prefix}' in value:
        return True
    s = VARIABLE_ANCHOR + '{' + prefix
    if s in value:
        return True if '}' in value[value.index(s) + len(s):] else False
    return False


def replace_all_variables(
        target: dict[str, any], source: Union[dict[str, any], None] = None) -> dict[str, any]:

    if not source:
        source = Env.load()

    target = copy.deepcopy(target)

    # We first replace all variables in the target, using values from the source
    __visit_all_variables(
        target, lambda variable, curr_path: __parse_variables_unscoped(variable, source))

    # We then replace all variables in the target, using values from the target
    __visit_all_variables(
        target, lambda variable, curr_path: parse_variables(variable, target, curr_path))

    def check_no_variable_left(text: str, _) -> str:
        if is_variable(text) and not is_action_variable(text):
            raise ValueError(f'Failed to replace variables in: {text}')
        return text

    __visit_all_variables(target, check_no_variable_left)

    return target


def __visit_all_variables(target: dict[str, any],
                          visit: Callable[[str, [str]], str],
                          path: [str] = None):
    # TODO - Implement 'me' expansion for $self related variables, test it too
    #  To achieve the above you need to implement the correct curr_path argument
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


def parse_variables(text: str, context: dict[str, any], curr_path: [str] = None) -> str:
    def replace(name: str) -> Union[str, None]:
        replacement = context.get(name)
        if replacement is None:
            replacement = __get_scoped_value_for_name_having_prefix(
                curr_path, name, SELF_KEY, context)
        return replacement

    return __parse_variables(text, replace)


def __parse_variables_unscoped(text: str, context: dict[str, any]) -> str:
    def replace(name: str) -> Union[str, None]:
        return context.get(name, None)

    return __parse_variables(text, replace)


def parse_run_arg(curr_path: [str], arg: str, run_context: 'RunContext' = None) -> any:
    if len(curr_path) != 3:
        raise ValueError(f'Expected 3 elements, found: {curr_path}')

    def replace(name: str) -> any:
        return __get_run_arg_value(curr_path, name, run_context, None)

    replacement = __parse_variables(arg, replace)

    if replacement is None:
        raise ValueError(f'Unsupported argument: {arg} for {".".join(curr_path)}')

    if is_variable(replacement):
        raise ValueError(
            f'Invalid replacement: {replacement} for: {arg} of {".".join(curr_path)}')

    return replacement


def __parse_variables(target: str, replace: Callable[[str], any]) -> str:
    if not is_variable(target):
        return target
    result = target
    pos = 0
    while pos < len(result):
        t: [str, int, int] = __extract_first_variable(result, pos, None)
        if t is None:
            break
        name = t[0]
        start = t[1]
        end = t[2]
        replacement = replace(name)
        # logger.debug(f'{name}, replacement: {replacement}')
        if replacement is None:
            pos = end
            continue
        result = result[0:start] + replacement + result[end:]
        pos = start + len(replacement)
    return result


def __get_run_arg_value(curr_path: [str],
                        name: str,
                        run_context: 'RunContext' = None,
                        result_if_none: Union[str, None] = None) -> Union[str, None]:
    replacement = None if run_context is None else run_context.get_arg(name)
    if replacement is None:
        replacement = __get_scoped_value_for_name_having_prefix(
            curr_path, name, CONTEXT_KEY, run_context)
        if replacement is None:
            replacement = __get_results_value(curr_path, name, run_context)
    return result_if_none if replacement is None else str(replacement)


def __get_scoped_value_for_name_having_prefix(
        curr_path: [str],
        name: str,
        prefix: str,
        context: Union['RunContext', dict] = None) -> Union[str, None]:
    def get_value(values_scope: any, key: str) -> any:
        if values_scope is None:
            return None if context is None else context.get(key, None)
        else:
            return values_scope.get(key, None)

    return __get_scoped_value(curr_path, name, prefix, get_value)


def __get_results_value(curr_path: [str],
                        name: str,
                        run_context: 'RunContext' = None) -> Union[str, None]:
    def get_value(scope: any, key: str) -> any:
        if scope is None:
            return None if run_context is None else run_context.get_stage_results(key, None)
        else:
            return scope.get(key, None)

    value = __get_scoped_value(curr_path, name, RESULTS_KEY, get_value)
    try:
        return None if value is None else value.get_result()
    except Exception:
        return value


def __get_scoped_value(curr_path: [str],
                       name: str,
                       prefix: str,
                       get_value: Callable[[any, str], any]) -> Union[str, None]:
    if not name.startswith(prefix):
        return None
    parts_including_prefix, index = __parse_index_part(name)
    parts = parts_including_prefix[1:]

    parts = __expand_me(curr_path, parts)

    scope = None
    for k in parts:
        try:
            scope = get_value(scope, k)
        except Exception as ex:
            raise ValueError(f'Value not found for: {k} of {name} in {scope}') from ex
        if scope is None:
            raise ValueError(f'Value not found for: {k} of {name} in {scope}')

    try:
        return scope[index] if isinstance(scope, list) else scope
    except IndexError as ex:
        raise IndexError(
            f'Invalid index: {index}, for variable: {name}, in scope: {scope}') from ex


def __expand_me(curr_path: [str], parts: [str]) -> [str]:
    if curr_path is None:
        return parts
    updated_parts: [str] = []
    for part in parts:
        if part == 'me':
            updated_parts.extend(curr_path)
        else:
            updated_parts.append(part)
    return updated_parts


def __parse_index_part(value: str) -> tuple[[str], int]:
    """
    highlight:: python
    code-block:: python
     Input: 'a.b.c[23]'
    Output: ([a, b, c], 23)
    """
    parts: [str] = value.split('.')
    last = parts[len(parts) - 1] if '.' in value else value
    if not last.endswith(']'):
        return parts, 0
    try:
        start: int = last.index('[')
        index_str: str = last[start + 1:len(last) - 1]
        index = int(index_str)
        parts[len(parts) - 1] = last[0:start]
        return parts, index
    except Exception as ex:
        raise ValueError(f'Invalid variable: {value}') from ex


def __extract_first_variable(
        text: str,
        offset: int = 0,
        result_if_none: Union[Tuple[str, int, int], None] = None) -> Tuple[str, int, int]:
    """
    highlight:: python
    code-block:: python
     Input: '${var} ${abc}'
    Output: ('var', 0, 6)
    """

    prefix = VARIABLE_ANCHOR

    try:
        start_idx: int = text.index(prefix, offset) + len(prefix)
        if text[start_idx] == '{':
            prefix = prefix + '{'
            start_idx += 1
    except ValueError:
        return result_if_none

    part: str = text[start_idx:]
    if '}' not in part:
        if ' ' not in part:
            return text[start_idx:], start_idx - len(prefix), len(text)
        else:
            last_char_is_space = True
            end_idx: int = text.index(' ', start_idx)
    else:
        last_char_is_space = False
        end_idx: int = text.index('}', start_idx)

    return (text[start_idx:end_idx],
            start_idx - len(prefix),
            end_idx if last_char_is_space else end_idx + 1)


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

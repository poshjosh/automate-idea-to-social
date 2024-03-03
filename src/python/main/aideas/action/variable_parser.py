import logging
from typing import Union, Tuple, Callable

RESULTS_KEY = 'results'
VARIABLE_ANCHOR = '$'

logger = logging.getLogger(__name__)


def is_variable(value: str) -> bool:
    if VARIABLE_ANCHOR in value:
        return True
    s = VARIABLE_ANCHOR + '{'
    if s in value:
        return True if '}' in value[value.index(s) + len(s):] else False
    return False


def is_results_variable(value: str) -> bool:
    if f'{VARIABLE_ANCHOR}{RESULTS_KEY}' in value:
        return True
    s = VARIABLE_ANCHOR + '{' + RESULTS_KEY
    if s in value:
        return True if '}' in value[value.index(s) + len(s):] else False
    return False


def visit_all_variables(context: dict[str, any], visit: Callable[[str], str]):

    def iter_dict(d: dict[str, any]):
        for k, v in d.items():
            d[k] = iter_value(v)
        return d

    def iter_list(e_list: list[any]):
        for i, e in enumerate(e_list):
            e_list[i] = iter_value(e)
        return e_list

    def iter_value(e: any):
        if isinstance(e, dict):
            return iter_dict(e)
        elif isinstance(e, list):
            return iter_list(e)
        elif isinstance(e, str):
            return visit(e)
        else:
            return e

    iter_dict(context)


def parse_variables(text: str, context: dict[str, any]) -> str:
    return __parse_variables(text, lambda key: context.get(key))


def parse_run_arg(curr_path: [str], arg: str, run_context: 'RunContext' = None) -> any:
    if not is_variable(arg):
        return arg

    if len(curr_path) != 3:
        raise ValueError(f'Expected 3 elements, found: {curr_path}')

    def replace(name: str) -> any:
        return __get_run_arg_replacement(curr_path, name, run_context, None)

    replacement = __parse_variables(arg, replace)

    if replacement is None:
        raise ValueError(f'Unsupported argument: {arg} for {".".join(curr_path)}')

    return replacement


def __parse_variables(text: str, replace: Callable[[str], any]) -> str:
    pos = 0
    while pos < len(text):
        t: [str, int, int] = __extract_first_variable(text, pos, None)
        if t is None:
            break
        name = t[0]
        start = t[1]
        end = t[2]
        replacement = replace(name)
        #logger.debug(f'{name}, replacement: {replacement}')
        if replacement is None:
            pos = end
            continue
        text = text[0:start] + replacement + text[end:]
        pos = start + len(replacement)
    return text


def __get_run_arg_replacement(curr_path: [str],
                              name: str,
                              run_context: 'RunContext' = None,
                              result_if_none: Union[str, None] = None) -> Union[str, None]:
    replacement = None if run_context is None else run_context.get_arg(name)
    if replacement is None:
        replacement = __parse_result(curr_path, name, run_context)
    return result_if_none if replacement is None else str(replacement)


def __parse_result(curr_path: [str], value: str, run_context: 'RunContext' = None) -> Union[str, None]:
    if not value.startswith(RESULTS_KEY):
        return None
    parts_including_results_key, index = __parse_index_part(value)
    parts = parts_including_results_key[1:]

    def get_value(values_scope: any, key: str) -> any:
        if values_scope is None:
            return None if run_context is None else run_context.get_stage_results(key, None)
        else:
            return values_scope.get(key, None)

    parts = __expand_me(curr_path, parts)

    scope = None
    for k in parts:
        try:
            scope = get_value(scope, k)
        except Exception as ex:
            raise ValueError(f'Value not found for: {k} of {value}') from ex
        if scope is None:
            raise ValueError(f'Value not found for: {k} of {value}')

    try:
        return scope[index].get_result()
    except IndexError as ex:
        raise IndexError(f'Invalid variable: {value} for scope: {scope}') from ex


def __expand_me(curr_path: [str], parts: [str]) -> [str]:
    updated_parts:[str] = []
    for part in parts:
        if part == 'me':
            updated_parts.extend(curr_path)
        else:
            updated_parts.append(part)
    return updated_parts


"""
..highlight:: python
.. code-block:: python
 Input: 'a.b.c[23]'
Output: ([a, b, c], 23)
"""


def __parse_index_part(value: str) -> tuple[[str], int]:
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


"""
..highlight:: python
.. code-block:: python
 Input: '${var} ${abc}'
Output: ('var', 0, 6)
"""


def __extract_first_variable(
        text: str,
        offset: int = 0,
        result_if_none: Union[Tuple[str, int, int], None] = None) -> Tuple[str, int, int]:
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

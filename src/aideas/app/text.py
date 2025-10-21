import uuid
import re
from re import Match


def list_from_str(value: str) -> list[str]:
    """
    Converts a string representation of a list into an actual list.
    Examples:
    - "['a', 'b', 'c']" -> ["a", "b", "c"]
    - 'a', 'b', 'c' -> ["a", "b", "c"]
    :param value: the string to convert
    :return: the list created from the string
    """
    if not value:
        return []
    if value.startswith('[') or value.endswith(']'):
        value = value[1:-1]
    return [e.strip() for e in split_preserving_quotes(value, ',', True)]


def split_preserving_quotes(text: str, separator: str = ' ', remove_quotes: bool = False) -> list:
    """
    Split a string around separators, but preserve quoted groups.

    Does not support quotes within quotes.

    The output list of strings is gotten by splitting the input strings around one or more occurrences of the separator.
    There is a catch: The splitting should not be applied to words which are grouped together.
    Words are grouped together if they start and end with either a double or a single quote.

    Args:
        text (str): The input string to split
        separator (str): The separator to split on (default is space)
        remove_quotes (bool): If True, remove quotes from the output strings (default is True)

    Returns:
        list: List of strings after splitting, with quoted groups preserved

    Example input and their corresponding outputs, given that remove_quotes is False:

        Input: first " " $TEXT_TITLE "#shorts"
    Seperator: ' '
       Output: ['first', '" "', '$TEXT_TITLE', '#shorts']

        Input: first_"_"__$TEXT_TITLE__"#shorts"
    Seperator: '_'
       Output: ['first', '"_"', '$TEXT_TITLE', '#shorts']

        Input: test-action ' a boy shorts' tinkerer
    Separator: ' '
       Output: ["test-action", "' a boy shorts'", "tinkerer"]

        Input: enter_text Never have I ever played the game: "Never have I ever" Drink to that!
    Separator: ' '
       Output: ['enter_text', 'Never have I ever played the game:', '"Never have I ever".', 'Drink to that!']

        Input: ''
    Separator: ' '
       Output:  ['']
    """
    if not text:
        return ['']

    replacements = {}

    text = _replace_all_list_format_strings(text, replacements)

    result_list = []
    current = ""
    in_single_quotes = False
    in_double_quotes = False
    i = 0

    while i < len(text):
        char = text[i]

        # Handle quote escaping
        if char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
            current += char
        elif char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
            current += char
        elif char == separator and not in_single_quotes and not in_double_quotes:
            # We found a separator outside of quotes
            result_list.append(current)
            current = ""
            # Skip consecutive separators
            while i + 1 < len(text) and text[i + 1] == separator:
                i += 1
        else:
            current += char

        i += 1

    # Add the last part
    result_list.append(current)

    result_list = __handle_special_case_of_only_separators(text, result_list, separator)

    result_list = __check_and_remove_quotes(result_list, remove_quotes)

    return _return_all_list_format_strings(result_list, replacements)


def _replace_all_list_format_strings(text: str, replacements: dict[str, str]) -> str:
    def get_replacement(match: Match) -> str:
        replacement = str(uuid.uuid4().hex)
        replacements[replacement] = match.group()
        return replacement

    # both r'\[.*?]' and r'\[[^]]*]' work; compiler prefers later
    return re.sub(r'\[[^]]*]', get_replacement, text)


def _return_all_list_format_strings(target: list, replacements: dict[str, str]) -> list:
    for replacement, original in replacements.items():
        for idx, e in enumerate(target):
            target[idx] = e.replace(replacement, original)
    return target


def __handle_special_case_of_only_separators(text: str, result: list, separator: str) -> list:
    if not any(result) and text and all(c == separator for c in text):
        return [''] * (text.count(separator) + 1)
    return result


def __check_and_remove_quotes(result: list[str], remove_quotes: bool = True) -> list:
    for index, e in enumerate(result):
        e = __check_and_remove_quote(e, '"', remove_quotes)
        e = __check_and_remove_quote(e, "'", remove_quotes)
        result[index] = e
    return result


def __check_and_remove_quote(part: str, quote: str, remove_quotes: bool = True) -> str:
    endings_allowed_after_quote = ['.', ',', '!', '?', ':', ';']
    if part.startswith(quote):
        if part.endswith(quote):
            return part[1:-1] if remove_quotes else part
        else:
            if any(part.endswith(ending) for ending in endings_allowed_after_quote):
                return part.replace(quote, "") if remove_quotes else part
            else:
                raise ValueError(f'Invalid value, missing closing quote for: {part}')
    else:
        if part.endswith(quote):
            raise ValueError(f'Invalid value, missing opening quote for: {part}')
        else:
            return part

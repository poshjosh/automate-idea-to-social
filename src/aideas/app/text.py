"""
SPECIFICATION

Function arguments:

- First argument is a string.
- Second argument is a string which is used as a separator (default is empty space) for splitting the first argument.
- Output a list of strings.

Function logic:

The output list of strings is gotten by splitting the input strings around one or more occurences of the separator.
There is a catch: The splitting should not be applied to words which are grouped together.
Words are grouped together if they start and end with either a double or a single quote.

Example input and their corresponding outputs:

    Input: first " " $TEXT_TITLE "#shorts"
Seperator: ' '
   Output: ['first', '" "', '$TEXT_TITLE', '#shorts']

    Input: first_"_"__$TEXT_TITLE__"#shorts"
Seperator: '_'
   Output: ['first', '"_"', '$TEXT_TITLE', '#shorts']

    Input: test-action ' a boy shorts' tinkerer
Separator: ' '
   Output: ["test-action", "' a boy shorts'", "tinkerer"]

    Input: enter_text Never have I ever played the game: "Never have I ever". Drink to that!
Separator: ' '
   Output: ['enter_text', 'Never have I ever played the game:', '"Never have I ever".', 'Drink to that!']

    Input: ''
Separator: ' '
   Output:  ['']
"""
def split_preserving_quotes(text: str, separator: str = ' ') -> list:
    """
    Split a string around separators, but preserve quoted groups.

    Args:
        text (str): The input string to split
        separator (str): The separator to split on (default is space)

    Returns:
        list: List of strings after splitting, with quoted groups preserved
    """
    if not text:
        return ['']

    result = []
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
            result.append(current)
            current = ""
            # Skip consecutive separators
            while i + 1 < len(text) and text[i + 1] == separator:
                i += 1
        else:
            current += char

        i += 1

    # Add the last part
    result.append(current)

    # Handle special case of only separators
    if not any(result) and text and all(c == separator for c in text):
        return [''] * (text.count(separator) + 1)

    return result

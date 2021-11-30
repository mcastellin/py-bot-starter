"""
A collection of useful functions
"""


def str2mdown(text):
    """
    Converts the given text string to Markdown .

    :param text: The string to be converted.
    :return: The Markdown converted text.
    """

    if text is None:
        return None
    else:
        return text.replace("-", "\\-") \
            .replace("!", "\\!") \
            .replace(".", "\\.") \
            .replace(">", "\\>") \
            .replace("_", "\\_")


def _break_pattern(ptn: str):
    if len(ptn) > 1:
        return "".join(["-" + c for c in ptn])
    else:
        raise ValueError("Separator pattern must contain at least two characters.")


def _escape_separator(text, separator):
    return text.replace(separator, _break_pattern(separator))


def _unescape_separator(text, separator):
    return text.replace(_break_pattern(separator), separator)


def pack_callback_data(action, params, separator):
    """
    A function to merge action name and parameters in a single string to be used as callback_data.

    :param action: the action name
    :param params: a list of action parameters
    :param separator: the separator pattern
    :return: a single string to be used as callback_data:
    """
    if separator in action:
        raise ValueError(f"Action name [{action}] cannot contain the string separator [{separator}]." +
                         "Choose a different action name.")
    escaped_params = [
        _escape_separator(p, separator)
        for p in params
    ]
    callback_data = separator.join([action, *escaped_params])
    return callback_data


def unpack_callback_data(value, separator):
    """
    A function to unpack merged callback options.
    :return:    a tuple with two values: the action string and a list of action parameters:
                "ACT::pram1::param2" -> returns -> ("ACT", ["param1", "param2"])
    """
    tokens = value.split(separator)
    if len(tokens) >= 1:
        callback_action = tokens[0]
        params = [
            _unescape_separator(p, separator)
            for p in tokens[1:]
        ]
        if len(callback_action) > 0:
            return callback_action, params
        else:
            raise ValueError("Could not unpack callback action! Action string is empty!")
    else:
        raise ValueError("Could not unpack callback action! Not enough tokens!")

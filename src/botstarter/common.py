import re


def str2mdown(text):
    """
    Converts the given text string to Markdown .

    Parameters:
        text (str): The string to be converted.

    Returns:
        str: The Markdown converted text.
    """

    return text.replace("-", "\\-") \
        .replace("!", "\\!") \
        .replace(".", "\\.") \
        .replace(">", "\\>") \
        .replace("_", "\\_")


def get_str_token(instr, idx=0):
    """
     Returns the token at the specified index of the instr.

     Parameters:
         instr (str): The tokens string.
         idx (int): The index of the token to be returned.

     Returns:
         str: The token at index idx of instr.
     """

    if instr and len(instr) > 0:
        tokens = instr.lower().split()
        if len(tokens) > idx:
            return tokens[idx]
        else:
            return None
    else:
        return None


def extract_args(msg):
    """
     Returns the args list from a message.

     Parameters:
         msg (str): The message string.

     Returns:
         list[str]: The arguments list.
     """

    return msg.split()[1:]


def extract_locale_string(locstring):
    """
     Extracts the locale string.

     Parameters:
         locstring (str): The string.

     Returns:
         str: The locale string.
     """

    if locstring is None:
        return None
    elif len(locstring) >= 2:
        return locstring.lower()[:2]
    else:
        return None


def mask_text(text, pattern=None):
    """
    Substitutes {answer} in the pattern string with the masked text.

     Parameters:
         text (str): The text string to be masked.
         pattern (str): The pattern string in which to insert the masked text.

     Returns:
         str: The pattern with masked text instead of {answer}.
     """

    masked = re.sub(r"\S", "*", text)
    if pattern:
        return pattern.format(answer=masked)
    else:
        return masked


def unwrap_answer(text):
    """
    Replaces autocorrected characters from users' replies
    :param text:
    :return:
    """
    return text.replace("—", "--")

import re


def str2mdown(text):
    return text.replace("-", "\\-") \
        .replace("!", "\\!") \
        .replace(".", "\\.") \
        .replace(">", "\\>") \
        .replace("_", "\\_")


def get_str_token(instr, idx=0):
    if instr and len(instr) > 0:
        tokens = instr.lower().split()
        if len(tokens) > idx:
            return tokens[idx]
        else:
            return None
    else:
        return None


def extract_args(msg):
    return msg.split()[1:]


def extract_locale_string(locstring):
    if locstring is None:
        return None
    elif len(locstring) >= 2:
        return locstring.lower()[:2]
    else:
        return None


def mask_text(text, pattern=None):
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

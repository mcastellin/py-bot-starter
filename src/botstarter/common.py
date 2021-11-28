"""
A collection of useful functions
"""


def str2mdown(text):
    """
    Converts the given text string to Markdown .

    Parameters:
        text (str): The string to be converted.

    Returns:
        str or None: The Markdown converted text.
    """
    if text is None:
        return None
    else:
        return text.replace("-", "\\-") \
                   .replace("!", "\\!") \
                   .replace(".", "\\.") \
                   .replace(">", "\\>") \
                   .replace("_", "\\_")

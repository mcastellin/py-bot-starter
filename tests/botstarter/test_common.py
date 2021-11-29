from botstarter.common import *


def test_str2mdown():
    str = "-!.>_"

    result = str2mdown(str)
    assert "\\-\\!\\.\\>\\_" == result, "Str was not converted to mdown correctly."


def test_empty_input_str2mdown():
    str = None

    result = str2mdown(str)
    assert result is None, "Empty input not handled correctly."

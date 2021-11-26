from botstarter.common import *


def test_unwrap_answer():
    user_input = "—opt"

    result = unwrap_answer(user_input)
    assert "--opt" == result, "User input was not unwrapped correctly."


def test_str2mdown():
    str = "-!.>_"

    result = str2mdown(str)
    assert "\\-\\!\\.\\>\\_" == result, "Str was not converted to mdown correctly."


def test_get_str_token():
    instr = "a b c d"

    result1 = get_str_token(instr, 2)
    result2 = get_str_token(instr, 4)
    result3 = get_str_token("")
    assert 'c' == result1, "Token was not extracted correctly."
    assert result2 is None, "Token index out of bounds wasn't handled correctly."
    assert result3 is None, "Empty string wasn't handled correctly."


def test_extract_args():
    msg = "args b c"

    result = extract_args(msg)
    assert ['b', 'c'] == result, "Args were not extracted correctly."


def test_extract_locale_string():
    locstring = "it_IT"
    short_locstring = "a"

    result1 = extract_locale_string(locstring)
    result2 = extract_locale_string(short_locstring)
    result3 = extract_locale_string(None)
    assert 'it' == result1, "Locale string was not extracted correctly."
    assert result2 is None, "Short string wasn't handled correctly."
    assert result3 is None, "None string wasn't handled correctly."


def test_mask_text():
    text = "a bc def"
    pattern = "Test pattern: {answer}"

    result1 = mask_text(text)
    result2 = mask_text(text, pattern)
    assert '* ** ***' == result1, "Text was not masked correctly."
    assert 'Test pattern: * ** ***' == result2, "Pattern was not formatted correctly."

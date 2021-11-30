import pytest

from botstarter import util


def test_str2mdown():
    text = "-!.>_"

    result = util.str2mdown(text)
    assert "\\-\\!\\.\\>\\_" == result, "Str was not converted to mdown correctly."


def test_empty_input_str2mdown():
    result = util.str2mdown(None)
    assert result is None, "Empty input not handled correctly."


def test_pack_callback_data():
    """Tests the function can pack action and parameters to a single callback_data string"""
    callback_data = util.pack_callback_data("ACTION", params=["1", "2"], separator="::")
    assert callback_data == "ACTION::1::2"


def test_pack_callback_data_should_escape_separator_chars():
    """Tests the function can pack callback_data string and escape separator if used in a parameter"""
    callback_data = util.pack_callback_data("ACTION", params=["some::param"], separator="::")
    assert callback_data == "ACTION::some-:-:param"


def test_pack_callback_data_should_error_if_separator_in_action_name():
    """Tests the function raises a ValueError if the action name contains the separator"""
    with pytest.raises(ValueError):
        util.pack_callback_data("ACT::ION", params=["p1", "p2"], separator="::")


def test__break_pattern_should_fail_with_one_char_separator():
    """
    Tests the _break_pattern function fails if the separator pattern has less than 2 character.
    The reason for enforcing this is because single-char separator patterns cannot be escaped correctly.
    """
    with pytest.raises(ValueError):
        util._break_pattern(".")


def test_unpack_callback_data():
    """Tests the function can unpack callback action with its parameters"""
    test_str = "action::1::2::param3"
    action, params = util.unpack_callback_data(test_str, separator="::")
    assert action == "action"
    assert params == ["1", "2", "param3"]


def test_unpack_callback_data_with_no_params():
    """Tests the function can unpack callback action when no parameters are supplied"""
    test_str = "action"
    action, params = util.unpack_callback_data(test_str, separator="::")
    assert action == "action"
    assert params == []


def test_unpack_callback_data_should_fail_with_empty_value():
    """Tests the function raises a ValueError when there is no action to unpack"""
    test_str = ""
    with pytest.raises(ValueError):
        util.unpack_callback_data(test_str, separator="::")


def test_unpack_callback_data_should_unescape_separators_in_params():
    """Tests the function can unpack callback_data and remove escaped separator strings"""
    test_str = "ACTION::some-:-:param"
    action, params = util.unpack_callback_data(test_str, separator="::")
    assert params == ["some::param"]


test_data = [
    ("echo", ["1", "2"], "--"),
    ("echo action", ["param 1", "my_paramet??er_2"], "??"),
    ("some other action", ["1", "2", "complicated\n\nparameter\n\nvalue"], "\n\n"),
    ("action::name", ["at the end::?:", "::?:at the start", "param::?:"], "::?:")
]


@pytest.mark.parametrize("action_name,action_params,separator", test_data)
def test_pack_unpack_should_return_same_value(action_name, action_params, separator):
    """
    Parameterised function to run a few scenarios through the pack-unpack process and verify
    the input strings are unaffected after this process.
    """
    packed = util.pack_callback_data(action_name, params=action_params, separator=separator)
    act, act_params = util.unpack_callback_data(packed, separator=separator)
    assert act == action_name
    assert act_params == action_params

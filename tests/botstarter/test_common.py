from botstarter.common import unwrap_answer


def test_unwrap_answer():
    user_input = "—opt"

    result = unwrap_answer(user_input)
    assert "--opt" == user_input, "User input was not unwrapped correctly."

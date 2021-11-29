import mock
import pytest

from botstarter import bot


@mock.patch("botstarter.bot.__bot")
def test_get_mock(bot_mock):
    """Tests get_bot() returned the initialized bot"""
    assert bot.get_bot() is bot_mock


def test_get_mock_should_raise_error_not_initialized():
    """Tests raises runtime error if bot was not initialized"""
    bot.__bot = None
    with pytest.raises(RuntimeError):
        bot.get_bot()

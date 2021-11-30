import os

import mock
import pytest

from botstarter import bot

TEST_TOKEN = "sometoken"


@mock.patch("telebot.TeleBot")
def test_init_bot_token_parameter(bot_mock):
    """Test bot token passed as parameter is used first"""
    os.environ["BOT_TOKEN"] = "someothertoken"
    bot.init_bot(token=TEST_TOKEN)
    bot_mock.assert_called_once_with(token=TEST_TOKEN, threaded=False, parse_mode='MarkdownV2')


@mock.patch("telebot.TeleBot")
def test_init_bot_token_getenv(bot_mock):
    """Test bot token is falls back to environment variable value"""
    os.environ["BOT_TOKEN"] = str(TEST_TOKEN)

    bot.init_bot()
    bot_mock.assert_called_once_with(token=TEST_TOKEN, threaded=False, parse_mode='MarkdownV2')


def test_init_bot_should_fail_if_no_token():
    """Test raise ValueError if bot token was not supplied"""
    os.environ.pop("BOT_TOKEN", default=None)

    with pytest.raises(ValueError):
        bot.init_bot()

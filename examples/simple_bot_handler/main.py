import logging

from telebot import types

from botstarter import bot
from botstarter.decorators import user_handler

logging.basicConfig(level=logging.INFO)


@user_handler(commands=["test"])
def test_handler(msg, user, **kwargs):
    bot.send_message(
        msg.chat.id,
        text=f"Hello {user.first_name}\nEcho: {msg.text}"
    )


if __name__ == '__main__':
    bot.set_my_commands([
        types.BotCommand(command="test", description="Tests this bot")
    ])
    bot.start()

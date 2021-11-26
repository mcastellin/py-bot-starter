import logging

from telebot import types

from botstarter import bot
from botstarter.decorators import user_handler

logging.basicConfig(level=logging.INFO)


@user_handler(commands=["echo"])
def echo_handler(msg, user, **kwargs):
    received_msg = msg.text.replace("/echo", "", 1).strip()
    if received_msg:
        reply = f"Hello {user.first_name}\nEcho: {received_msg}"
    else:
        reply = "Didn't get any message to echo.\nTry with this command: `/echo ping`"

    bot.send_message(
        msg.chat.id,
        text=reply
    )


if __name__ == '__main__':
    bot.set_my_commands([
        types.BotCommand(command="echo", description="Echo a message back to the user")
    ])
    bot.start()

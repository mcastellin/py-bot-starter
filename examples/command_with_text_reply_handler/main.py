import logging

from telebot import types

from botstarter import bot

logging.basicConfig(level=logging.INFO)

bot.init_bot()


@bot.user_handler(commands=["echo"])
def echo_handler(msg, user, **kwargs):
    bot.wait_on_user_reply(user, "echo_action")
    bot.send_message(
        msg.chat.id,
        text="What message should I echo?"
    )


@bot.user_msg_callback(action="echo_action")
def echo_msg_callback_handler(msg, user, params, **kwargs):
    reply = f"Hello {user.first_name}\nEcho: {msg.text}"
    bot.send_message(
        msg.chat.id,
        text=reply
    )


if __name__ == '__main__':
    bot.set_my_commands([
        types.BotCommand(command="echo", description="Echo a message back to the user")
    ])
    bot.start()

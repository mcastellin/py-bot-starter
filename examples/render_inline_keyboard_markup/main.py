import logging

from telebot import types

from botstarter import bot

logging.basicConfig(level=logging.INFO)

bot.init_bot()

MOOD_ACTION = "mood"


def _gen_mood_markup():
    markup = types.InlineKeyboardMarkup(row_width=4)
    markup.add(
        bot.gen_inline_keyboard_btn(MOOD_ACTION, "🤩", "elated"),
        bot.gen_inline_keyboard_btn(MOOD_ACTION, "🙂", "happy"),
        bot.gen_inline_keyboard_btn(MOOD_ACTION, "😵‍💫", "stunned"),
        bot.gen_inline_keyboard_btn(MOOD_ACTION, "😰", "worried"),
    )

    return markup


def _motivate(mood):
    if mood == "elated":
        return "Other people feel good just by looking at you! ⭐️"
    elif mood == "happy":
        return "Keep it up! Life's good 😊"
    elif mood == "stunned":
        return "It's important to take a break every once in a while. Have a short walk and recharge your 🔋"
    elif mood == "worried":
        return "Everything's going to be ok 😃"


@bot.user_handler(commands=["mood"])
def mood_handler(msg, user, **kwargs):
    bot.send_message(
        msg.chat.id,
        text=f"Hello, {user.first_name}, what mood are you in today?",
        reply_markup=_gen_mood_markup()
    )


@bot.callback_response(action=MOOD_ACTION)
def mood_callback_handler(call, user, params):
    mood = params[0]
    quote_text = _motivate(mood)

    bot.edit_message_reply_markup(edit_msg=call.message, reply_markup=None)

    bot.send_message(
        call.message.chat.id,
        text=quote_text
    )


if __name__ == '__main__':
    bot.set_my_commands([
        types.BotCommand(command="mood", description="Tell me what your mood is")
    ])
    bot.start()

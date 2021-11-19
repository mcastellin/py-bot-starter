import logging
import os
from time import sleep

import telebot
from requests.exceptions import ReadTimeout
from telebot.types import BotCommand

from botstarter.common import str2mdown

# todo: disable send media for now until we have a working db implementation
# from db.medias import create_media, get_media_by_path

RETRY_TIMEOUT_INCREASE = 20
bot_token = os.getenv("BOT_TOKEN", default=None)

__bot = None


def get_bot() -> telebot.TeleBot:
    global __bot
    if not __bot:
        # telebot.logger.setLevel(logging.ERROR)
        __bot = telebot.TeleBot(
            bot_token,
            threaded=False,
            parse_mode="MarkdownV2"
        )

    return __bot


def __wrap_call(func, **kwargs):
    timeout = kwargs.pop("timeout")
    if not timeout:
        timeout = 20

    try:
        return func(**kwargs, timeout=timeout)
    except ReadTimeout:
        logging.debug("Telegram function call timed out. Re-trying with %d seconds timeout...", timeout)
        sleep(2)
        return func(**kwargs, timeout=timeout + RETRY_TIMEOUT_INCREASE)


def __wrap_text(text):
    if text:
        return str2mdown(text)
    else:
        return None


def send_typing(chat_id, timeout=10):
    get_bot().send_chat_action(chat_id, "typing", timeout)


def send_message(chat_id, text, reply_markup=None, timeout=20, **kwargs):
    logging.debug("Sending message to user with id %d", chat_id)
    return __wrap_call(
        get_bot().send_message,
        chat_id=chat_id,
        text=__wrap_text(text),
        reply_markup=reply_markup,
        timeout=timeout,
        **kwargs
    )


def reply_to(reply_to_msg, text, reply_markup=None, timeout=20):
    logging.debug("Sending reply to msg to user with id %d", reply_to_msg.from_user.id)
    return __wrap_call(
        get_bot().reply_to,
        message=reply_to_msg,
        text=__wrap_text(text),
        reply_markup=reply_markup,
        timeout=timeout
    )


def edit_message_reply_markup(edit_msg, reply_markup=None):
    logging.debug("Updating msg markup to user with id %d", edit_msg.from_user.id)
    get_bot().edit_message_reply_markup(
        chat_id=edit_msg.chat.id,
        message_id=edit_msg.message_id,
        reply_markup=reply_markup
    )


def edit_message_text(edit_msg, text, **kwargs):
    logging.debug("Updating msg text to user with id %d", edit_msg.from_user.id)
    return get_bot().edit_message_text(
        chat_id=edit_msg.chat.id,
        text=__wrap_text(text),
        message_id=edit_msg.message_id,
        **kwargs
    )


def edit_message_id_text(chat_id, message_id, text, **kwargs):
    logging.debug("Updating msg text to chat with id %d", chat_id)
    return get_bot().edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=__wrap_text(text),
        **kwargs
    )


def answer_callback_query(call, text=None, show_alert=False):
    logging.debug("Answering callback query to user %d", call.message.from_user.id)
    get_bot().answer_callback_query(
        call.id,
        text=__wrap_text(text),
        show_alert=show_alert
    )


def send_venue(chat_id, latitude, longitude, title, address, timeout=20, **kwargs):
    logging.debug(f"Sending venue to user with id %d", chat_id)
    __wrap_call(
        get_bot().send_venue,
        chat_id=chat_id,
        latitude=latitude,
        longitude=longitude,
        title=title,
        address=address,
        timeout=timeout,
        **kwargs
    )


def send_photo(chat_id, photo, timeout=30):
    logging.debug(f"Sending photo to user with id %d", chat_id)
    return __wrap_call(
        get_bot().send_photo,
        chat_id=chat_id,
        photo=photo,
        timeout=timeout
    )


# todo: disable send media for now until we have a working db implementation
# def send_or_upload_photo(chat_id, photo_path, timeout=30):
#     logging.debug(f"Sending photo to user with id %d", chat_id)
#
#     media = get_media_by_path(photo_path)
#     if media:
#         send_photo(
#             chat_id,
#             photo=media.upload_id,
#             timeout=timeout
#         )
#     else:
#         logging.debug("Uploading welcome photo.")
#         result = send_photo(
#             chat_id,
#             photo=open(photo_path, "rb"),
#             timeout=timeout
#         )
#         create_media(photo_path, result.photo[0].file_id)


def delete_message(message=None, chat_id=None, message_id=None, timeout=20):
    if message:
        _chat_id = message.chat.id
        _message_id = message.message_id
    else:
        _chat_id = chat_id
        _message_id = message_id

    if _chat_id and _message_id:
        logging.debug("Deleting message for chat with id %d", _chat_id)
        __wrap_call(
            get_bot().delete_message,
            chat_id=_chat_id,
            message_id=_message_id,
            timeout=timeout
        )
    else:
        raise Exception("Both message and (chat_id,message_id) are None. One must be defined to delete the message.")


def __gen_commands_global():
    return [
        BotCommand("testme", "Start a new game"),
        BotCommand("help", "Show help string"),
        BotCommand("start", "Show welcome message"),
    ]


def send_set_commands():
    get_bot().set_my_commands(
        commands=__gen_commands_global(),
        language_code=None
    )

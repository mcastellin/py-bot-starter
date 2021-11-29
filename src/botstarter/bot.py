import logging
import os
from time import sleep
from typing import List, Optional

import telebot
from requests.exceptions import ReadTimeout
from telebot import types

from botstarter.common import str2mdown
from botstarter.db import users, medias

RETRY_TIMEOUT_INCREASE = 20

__bot = None


def init_bot(db_opts=None, token=None, parse_mode="MarkdownV2", **kwargs) -> telebot.TeleBot:
    from botstarter.db.base import init_db
    if db_opts is None:
        db_opts = {}
    init_db(**db_opts)

    p_bot_token = token or os.getenv("BOT_TOKEN", default=None)
    global __bot
    __bot = telebot.TeleBot(
        token=p_bot_token,
        threaded=False,
        parse_mode=parse_mode,
        **kwargs
    )
    return __bot


def get_bot() -> telebot.TeleBot:
    global __bot
    if __bot:
        return __bot
    else:
        # todo: provide instructions on how to properly initialise the bot
        raise RuntimeError("Bot has not been initialized.")


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


def __wrap_text(text, parse_mode=None):
    if text:
        if parse_mode == "MarkdownV2":
            return str2mdown(text)
        else:
            return text
    else:
        return None


def send_typing(chat_id, timeout=10):
    get_bot().send_chat_action(chat_id, "typing", timeout)


def send_message(chat_id, text, reply_markup=None, timeout=20, **kwargs):
    logging.debug("Sending message to user with id %d", chat_id)
    return __wrap_call(
        get_bot().send_message,
        chat_id=chat_id,
        text=__wrap_text(text, get_bot().parse_mode),
        reply_markup=reply_markup,
        timeout=timeout,
        **kwargs
    )


def reply_to(reply_to_msg, text, reply_markup=None, timeout=20):
    logging.debug("Sending reply to msg to user with id %d", reply_to_msg.from_user.id)
    return __wrap_call(
        get_bot().reply_to,
        message=reply_to_msg,
        text=__wrap_text(text, get_bot().parse_mode),
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
        text=__wrap_text(text, get_bot().parse_mode),
        message_id=edit_msg.message_id,
        **kwargs
    )


def edit_message_id_text(chat_id, message_id, text, **kwargs):
    logging.debug("Updating msg text to chat with id %d", chat_id)
    return get_bot().edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=__wrap_text(text, get_bot().parse_mode),
        **kwargs
    )


def answer_callback_query(call, text=None, show_alert=False):
    logging.debug("Answering callback query to user %d", call.message.from_user.id)
    get_bot().answer_callback_query(
        call.id,
        text=__wrap_text(text, get_bot().parse_mode),
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


def send_or_upload_photo(chat_id, photo_path, timeout=30):
    logging.debug("Sending photo to user with id %d", chat_id)

    media = medias.get_media_by_path(photo_path)
    if media:
        send_photo(
            chat_id,
            photo=media.upload_id,
            timeout=timeout
        )
    else:
        logging.debug("Uploading photo with path %s", photo_path)
        result = send_photo(
            chat_id,
            photo=open(photo_path, "rb"),
            timeout=timeout
        )
        medias.create_media(photo_path, result.photo[0].file_id)


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


def set_my_commands(commands: List[types.BotCommand],
                    scope: Optional[types.BotCommandScope] = None,
                    language_code: Optional[str] = None) -> bool:
    return get_bot().set_my_commands(commands, scope, language_code)


# todo: callback_action separator should be escaped and un-escaped if present in action string value
CALLBACK_ACTION_SPLIT_SEPARATOR = "::"

ALL_WAITING_ON_CALLBACKS = {}


def admin_handler(commands):
    """
    Creates a new message handler for bot admin requests.

    :param commands: the message handler commands
    :return:
    """

    def function_decorator(func):
        bot = get_bot()

        @bot.message_handler(commands=commands)
        def check_message_from_admin(*args, **kwargs):
            msg = args[0]
            user_id = msg.from_user.id
            secure_chat_id = msg.from_user.id
            user = users.get_user_by_id(msg.from_user.id)

            logging.info(f"admin request from user with id {user_id}")
            if user is not None and bool(user.is_admin):
                logging.info(f"admin request GRANTED to user {user_id}")
                return func(*args, user_id, secure_chat_id, **kwargs)
            else:
                logging.info(f"admin request was DENIED for user with id {user_id}")
                return

        return check_message_from_admin

    return function_decorator


def user_handler(*args, **kwargs):
    """
    Registers a message handler for user requests.

    :return: the wrapper decorator function
    """

    def wrapper(wrapped_func):
        bot = get_bot()

        @bot.message_handler(*args, **kwargs)
        def load_user_information(msg):
            logging.debug("Received user request: %s", msg)

            if msg.from_user.is_bot:
                # do nothing if you receive a message from a bot
                logging.debug("Received message from bot. Discarding. %s", msg)
                return

            user = users.get_user_by_id(msg.from_user.id)
            if not user:
                logging.debug("User with id %s was not found in the system. Creating new user.", msg.from_user.id)
                user = users.create_user(msg)

            additional_args = {}
            if user.waiting_on:
                logging.debug("Bot was waiting on user's text reply: %s", user.waiting_on)
                waiting_tokens = user.waiting_on.split(CALLBACK_ACTION_SPLIT_SEPARATOR)
                additional_args['action_name'] = waiting_tokens[0]
                additional_args['action_params'] = waiting_tokens[1:]
                # remove waiting on option once read
                users.set_user_waiting_on(msg.from_user.id, waiting_on=None)

            return wrapped_func(msg, user, **additional_args)

        return load_user_information

    return wrapper


def gen_callback_option(callback_action, label, *values):
    payload = CALLBACK_ACTION_SPLIT_SEPARATOR.join(values)
    ss = str(CALLBACK_ACTION_SPLIT_SEPARATOR)
    action_string = f"{callback_action}{ss}{payload}"
    return [label, action_string]


def __unpack_callback_option(value):
    tokens = value.split(CALLBACK_ACTION_SPLIT_SEPARATOR)
    if len(tokens) >= 2:
        callback_action = tokens[0]
        values = tokens[1:]
        return callback_action, values
    else:
        raise ValueError("Could not unpack callback option!")


def callback_response(action, admin_only=False):
    """
    Registers a handler for the callback action specified in the parameters. It is also possible to secure the callback
    handler for admin use only with the `admin_only` flag.

    :param action: the callback action name
    :param admin_only: callback function is restricted and can only be run in response to messages coming from admins. Default is `False`
    :return: the decorator wrapper function
    """

    def wrapper(func):
        bot = get_bot()

        @bot.callback_query_handler(func=lambda call: call.data.startswith(f"{action}:"))
        def read_callback_response(call):
            logging.debug("Received callback action: %s", call)

            callback_action, values = __unpack_callback_option(call.data)
            logging.debug("Unpacked values for callback: action=%s, values=%s", callback_action, values)

            user_id = call.from_user.id
            if admin_only and not users.is_admin(user_id):
                logging.warning(f"Received admin request from non-admin user with id {user_id}")
                answer_callback_query(call)
                delete_message(message=call.message)
                return

            user = users.get_user_by_id(user_id)

            answer_callback_query(call)
            return func(call, user, values)

        return read_callback_response

    return wrapper


def user_msg_callback(action: str):
    """
    This decorator registers the decorated function as a message callback handler.

    :param action: the name of the action the bot awaits from users
    :return: the decorator wrapper function
    """

    def wrapper(func):
        ALL_WAITING_ON_CALLBACKS[action] = func

    return wrapper


def wait_on_user_reply(user: users.User, action: str, *action_params: str):
    """
    Wait for user's text reply on an action.

    :param user: the user object
    :param action: the name of the callback action
    :param action_params: any number of parameters for the wait-on action
    """
    if not user or user.id is None:
        raise ValueError("Could not wait on user text reply. User object is None or the user does not have an id.")
    if not action or len(action.strip()) == 0:
        raise ValueError("Could not wait on user text reply. Action name was not specified.")

    action_tokens = [action, *action_params]
    users.set_user_waiting_on(
        user_id=user.id,
        waiting_on=CALLBACK_ACTION_SPLIT_SEPARATOR.join(action_tokens)
    )


def _init_decorators():
    """
    Decorators initialization function. Some decorators, like the "catch-all" handler need to be registered last
    in order be the the very last handler to intercept users' requests.
    """

    @user_handler(func=lambda msg: True, content_types=["text"])
    def catch_all(msg, user, action_name=None, action_params=None, **kwargs):
        logging.debug("Running catch all. action_name=%s, action_params=%s, user=%d",
                      action_name, action_params, user.get("id"))

        if action_name is not None and action_name in ALL_WAITING_ON_CALLBACKS.keys():
            func = ALL_WAITING_ON_CALLBACKS.get(action_name)
            func(msg, user, action_params, **kwargs)


def start():
    """
    Initialize the bot and start polling Telegram API for new messages.
    """
    _init_decorators()

    logging.info("Starting Telegram bot!")
    get_bot().infinity_polling()

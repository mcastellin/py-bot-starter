import logging

from botstarter.bot import answer_callback_query, delete_message, get_bot
from botstarter.db.users import get_user_by_id, create_user, set_user_waiting_on, is_admin

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
            user = get_user_by_id(msg.from_user.id)

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

            user = get_user_by_id(msg.from_user.id)
            if not user:
                user = create_user(msg)

            additional_args = {}
            if user.waiting_on:
                waiting_tokens = user.waiting_on.split(CALLBACK_ACTION_SPLIT_SEPARATOR)
                additional_args['action_name'] = waiting_tokens[0]
                additional_args['action_params'] = waiting_tokens[1:]
                # remove waiting on option once read
                set_user_waiting_on(msg.from_user.id, waiting_on=None)

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
            if admin_only and not is_admin(user_id):
                logging.warning(f"Received admin request from non-admin user with id {user_id}")
                answer_callback_query(call)
                delete_message(message=call.message)
                return

            user = get_user_by_id(user_id)

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


def _init_decorators():
    @user_handler(func=lambda msg: True, content_types=["text"])
    def catch_all(msg, user, waiting_on=None, waiting_on_params=None, **kwargs):
        logging.debug("Running catch all. waiting_on=%s, waiting_on_params=%s, user=%d",
                      waiting_on, waiting_on_params, user.get("id"))

        if waiting_on is not None and waiting_on in ALL_WAITING_ON_CALLBACKS.keys():
            func = ALL_WAITING_ON_CALLBACKS.get(waiting_on)
            func(msg, user, waiting_on_params, **kwargs)

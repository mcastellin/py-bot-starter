import logging
import os
from enum import Enum
from importlib import import_module

from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database

__db = None

DEFAULT_DATABASE = "pybotstarter"


# todo: the global_init function should also accept database configuration as parameters, then fallback
# todo:     to environment variables.
def _global_init(database_name=None):
    global __db
    if __db:
        return

    # todo
    # p_host
    # p_port
    # p_username
    # p_password
    p_database_name = database_name or os.getenv("DATABASE_NAME")
    if not p_database_name:
        p_database_name = DEFAULT_DATABASE

    if os.getenv("MONGODB_USERNAME") and os.getenv("MONGODB_PASSWORD"):
        auth = {
            "username": os.getenv("MONGODB_USERNAME"),
            "password": os.getenv("MONGODB_PASSWORD")
        }
    else:
        auth = {}

    client = MongoClient(
        host=os.getenv("MONGODB_HOST", "localhost"),
        port=27017,
        **auth
    )
    __db = client[p_database_name]


def get_db() -> Database:
    global __db
    if not __db:
        _global_init()

    return __db


def init_db():
    parent_mod = "db"
    modules = os.listdir(parent_mod)
    for m in [mod.replace(".py", "") for mod in modules if mod.endswith(".py")]:
        logging.debug("Loading db module %s", m)
        import_module(f"{parent_mod}.{m}")


MODEL_INTERCEPTORS = {}
MODEL_CLASSES = {}


class InterceptorHooks(Enum):
    SAVE_USER_CREATE = "save_user_create"


def register_model(name):
    def wrapper(cls):
        MODEL_CLASSES[name] = cls
        cls.__collection_name__ = name
        cls.__collection__ = get_db()[name]
        return cls

    return wrapper


def model_interceptor(hook):
    def wrapper(func):
        MODEL_INTERCEPTORS[hook] = func
        logging.debug("Registered model interceptor for hook %s", hook)

        return func

    return wrapper


def get_interceptors(hook_name):
    return MODEL_INTERCEPTORS.get(hook_name)


class Base(dict):
    __collection__ = None

    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    @classmethod
    def get_doc(cls, object_id):
        doc = cls.__collection__.find_one({"_id": ObjectId(object_id)})
        return cls(doc)

    @classmethod
    def find_one(cls, *args, **kwargs):
        doc = cls.__collection__.find_one(*args, **kwargs)
        if doc:
            return cls(doc)

    @classmethod
    def update_one(cls, *args, **kwargs):
        return cls.__collection__.update_one(*args, **kwargs)

    def save(self):
        if not self._id:
            res = self.__collection__.insert_one(self)
            self['_id'] = res.inserted_id
        else:
            self.__collection__.update_one({"_id": ObjectId(self._id)}, self)

    def reload(self):
        if self._id:
            self.update(self.__collection__.find_one({"_id": ObjectId(self._id)}))

    def remove(self):
        if self._id:
            self.__collection__.remove({"_id": ObjectId(self._id)})
            self.clear()

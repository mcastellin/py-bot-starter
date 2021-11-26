import logging
import os
from enum import Enum
from importlib import import_module
from os.path import isdir

from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database

__db = None

DEFAULT_DATABASE = "pybotstarter"


class Base(dict):
    __collection__ = None

    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    @classmethod
    def get_doc(cls, object_id):
        doc = cls.__collection__.find_one({"_id": ObjectId(object_id)})
        if doc:
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


def get_db() -> Database:
    global __db
    if __db:
        return __db
    else:
        raise RuntimeError("""
Database was not initialised. To fix this issue add the following lines to your main python file:

from botstarter.db.base import init_db

if __name__ == "__main__":
    init_db()""")


MODEL_INTERCEPTORS = {}
MODEL_CLASSES = {}


class InterceptorHooks(Enum):
    SAVE_USER_CREATE = "save_user_create"


def register_model(name):
    def wrapper(cls):
        MODEL_CLASSES[name] = cls
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


def __create_models():
    for collection in MODEL_CLASSES.keys():
        cls = MODEL_CLASSES.get(collection)
        cls.__collection_name__ = collection
        cls.__collection__ = get_db()[collection]


def __load_db_modules_extensions():
    # todo: walk db packages using pkgutil, for now using a workaround
    # import pkgutil
    # for loader, module_name, is_pkg in pkgutil.walk_packages(botstarter.db.__path__):
    #     print(module_name)
    import_module("botstarter.db.medias")
    import_module("botstarter.db.users")

    caller_db_modules_dir = "db"
    if isdir(caller_db_modules_dir):
        modules = os.listdir(caller_db_modules_dir)
        for m in [mod.replace(".py", "") for mod in modules if mod.endswith(".py") and mod != "__init__.py"]:
            logging.debug("Loading db module %s", m)
            import_module(f"{caller_db_modules_dir}.{m}")


def init_db(host=None, port=None, database_name=None, auth=None):
    global __db
    if __db:
        return

    p_host = host or os.getenv("MONGODB_HOST", "localhost")
    p_port = port or os.getenv("MONGODB_PORT", 27017)
    p_database_name = database_name or os.getenv("DATABASE_NAME", DEFAULT_DATABASE)

    if not auth:
        if os.getenv("MONGODB_USERNAME") and os.getenv("MONGODB_PASSWORD"):
            auth = {
                "username": os.getenv("MONGODB_USERNAME"),
                "password": os.getenv("MONGODB_PASSWORD")
            }
        else:
            auth = {}

    client = MongoClient(
        host=p_host,
        port=p_port,
        **auth
    )
    __db = client[p_database_name]
    __load_db_modules_extensions()
    __create_models()

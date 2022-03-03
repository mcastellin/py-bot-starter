import logging
import os
from enum import Enum
from importlib import import_module
from os.path import isdir
from typing import List, TypeVar, Optional

import pymongo
from bson import ObjectId
from pymongo import database
from pymongo.database import Collection
from pymongo.results import UpdateResult, DeleteResult

__db: database.Database = None

DEFAULT_DATABASE = "pybotstarter"

TBase = TypeVar("TBase", bound="Base")


class Base(dict):
    __collection__: Collection = None

    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    @classmethod
    def get_doc(cls, object_id) -> TBase:
        doc = cls.__collection__.find_one({"_id": ObjectId(object_id)})
        if doc:
            return cls(doc)

    @classmethod
    def find(cls, *args, **kwargs) -> List[TBase]:
        docs = cls.__collection__.find(*args, **kwargs)
        if docs:
            return [cls(doc) for doc in docs]

    @classmethod
    def find_one(cls, *args, **kwargs) -> TBase:
        doc = cls.__collection__.find_one(*args, **kwargs)
        if doc:
            return cls(doc)

    @classmethod
    def update_one(cls, *args, **kwargs) -> UpdateResult:
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

    def remove(self) -> Optional[DeleteResult]:
        if self._id:
            result = self.__collection__.delete_one({"_id": ObjectId(self._id)})
            self.clear()
            return result
        else:
            return None


def get_db() -> database.Database:
    global __db
    if __db is not None:
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
    """
    Initializes the database connection with MongoDB.
    Parameters for the connection can be set using function parameters or environment variables. Every time a
    parameter is supplied directly to the function, it will override whatever is defined as an environment variables.
    In essence, environment variables are used as "fallback values" for missing parameters.

    :param: host: the db hostname. Default is "localhost". Can also be set with "MONGODB_HOST" environment variable
    :param: port: the db port. Default is "27017". Can also be set with "MONGODB_PORT" environment variable
    :param: database_name: the name of the database. Default is "pybotstarter". Can also be set with "DATABASE_NAME" environment variable
    :param: auth:   a dict containing the "username" and "password" keys for authentication. If left empty,
                    no authentication is used. To set authentication with environment variables, both "MONGODB_USERNAME"
                    and "MONGODB_PASSWORD" environment variables must be defined. If not a ValueError is raised.


    """
    global __db

    p_host = host or os.getenv("MONGODB_HOST", "localhost")
    p_port = port or os.getenv("MONGODB_PORT", 27017)
    p_database_name = database_name or os.getenv("DATABASE_NAME", DEFAULT_DATABASE)

    if not auth:
        env_username = os.getenv("MONGODB_USERNAME")
        env_password = os.getenv("MONGODB_PASSWORD")
        if env_username and env_password:
            auth = {
                "username": env_username,
                "password": env_password
            }
        elif not env_username and not env_password:
            auth = {}
        else:
            raise ValueError(
                "Only one authentication variable is set. Please provide both MONGODB_USERNAME and MONGODB_PASSWORD.")

    client = pymongo.MongoClient(
        host=p_host,
        port=int(p_port),
        **auth
    )
    __db = client[p_database_name]
    __load_db_modules_extensions()
    __create_models()

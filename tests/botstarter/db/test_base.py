import os

import mock
import pytest

from botstarter.db.base import init_db

MONGODB_DEFAULT_HOST = "localhost"
MONGODB_DEFAULT_PORT = 27017


@mock.patch("pymongo.MongoClient")
def test_base_init_db_default_connection_parameters(mongo_client):
    """Tests mongodb connection is setup with default parameters if none are provided"""
    init_db()

    mongo_client.assert_called_once_with(host=MONGODB_DEFAULT_HOST, port=MONGODB_DEFAULT_PORT)


@mock.patch("pymongo.MongoClient")
def test_base_init_db_should_use_env_variables(mongo_client):
    """Tests mongodb connection is setup with all values from environment variables"""
    os.environ["MONGODB_HOST"] = "somehost"
    os.environ["MONGODB_PORT"] = "12345"
    os.environ["DATABASE_NAME"] = "somedatabase"
    os.environ["MONGODB_USERNAME"] = "someuser"
    os.environ["MONGODB_PASSWORD"] = "somepass"

    init_db()

    mongo_client.assert_called_once_with(
        host="somehost",
        port=12345,
        username="someuser",
        password="somepass"
    )
    mongo_client.return_value.__getitem__.assert_called_once_with("somedatabase")


@mock.patch("pymongo.MongoClient")
def test_base_init_db_should_use_parameters_over_env_variables(mongo_client):
    """
    Tests mongodb connection is setup with values from function parameters
    rather then environment variables
    """
    os.environ["MONGODB_HOST"] = "wronghost"
    os.environ["MONGODB_PORT"] = "00000"
    os.environ["DATABASE_NAME"] = "wrongdb"
    os.environ["MONGODB_USERNAME"] = "wronguser"
    os.environ["MONGODB_PASSWORD"] = "wrongpass"

    auth = {
        "username": "someuser",
        "password": "somepass"
    }
    init_db(host="somehost", port=12345, auth=auth, database_name="somedatabase")

    mongo_client.assert_called_once_with(
        host="somehost",
        port=12345,
        username="someuser",
        password="somepass"
    )
    mongo_client.return_value.__getitem__.assert_called_once_with("somedatabase")


def test_base_init_db_should_fail_if_only_username_set():
    """Tests the mongodb client init fails if only authentication password environment variable is set"""
    os.environ["MONGODB_PASSWORD"] = "somepass"
    os.environ.pop("MONGODB_USERNAME", default=None)

    with pytest.raises(ValueError):
        init_db()


def test_base_init_db_should_fail_if_only_password_set():
    """Tests the mongodb client init fails if only authentication username environment variable is set"""
    os.environ["MONGODB_USERNAME"] = "someuser"
    os.environ.pop("MONGODB_PASSWORD", default=None)

    with pytest.raises(ValueError):
        init_db()

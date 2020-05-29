from unittest.mock import MagicMock
from typing import Type
import os

import pytest
from datajoint.connection import Connection
from datajoint.schemas import Schema

from link import schemas


def test_if_schema_cls_is_correct():
    assert schemas.LazySchema._schema_cls is Schema


@pytest.fixture
def schema_name():
    return "schema_name"


@pytest.fixture
def connection():
    return MagicMock(name="connection", spec=Connection)


def test_if_value_error_is_raised_if_initialized_with_connection_and_host(connection):
    with pytest.raises(ValueError):
        schemas.LazySchema(schema_name, connection=connection, host="host")


@pytest.fixture
def schema_cls():
    return MagicMock(name="schema_cls", spec=Type[Schema])


@pytest.fixture
def lazy_schema_cls(schema_cls):
    schemas.LazySchema._schema_cls = schema_cls
    return schemas.LazySchema


class TestInitialize:
    @pytest.fixture
    def context(self):
        return dict()

    @pytest.fixture
    def setup_env(self):
        os.environ.update(REMOTE_DJ_USER="user", REMOTE_DJ_PASS="pass")

    @pytest.fixture
    def conn_cls(self, connection):
        return MagicMock(name="conn_cls", spec=Type[Connection], return_value=connection)

    @pytest.fixture
    def lazy_schema_cls(self, lazy_schema_cls, conn_cls):
        lazy_schema_cls._conn_cls = conn_cls
        return lazy_schema_cls

    @pytest.mark.usefixtures("setup_env")
    def test_if_connection_cls_is_correctly_initialized_if_host_is_provided(
        self, lazy_schema_cls, schema_name, conn_cls
    ):
        lazy_schema_cls(schema_name, host="host").initialize()
        conn_cls.assert_called_once_with("host", "user", "pass")

    @pytest.mark.usefixtures("setup_env")
    def test_if_connection_is_passed_to_schema_if_host_is_provided(
        self, lazy_schema_cls, schema_name, connection, schema_cls
    ):
        lazy_schema_cls(schema_name, host="host").initialize()
        schema_cls.assert_called_once_with(
            schema_name=schema_name, context=None, connection=connection, create_schema=True, create_tables=True
        )

    def test_if_schema_name_is_passed(self, lazy_schema_cls, schema_name, schema_cls):
        lazy_schema_cls(schema_name).initialize()
        schema_cls.assert_called_once_with(
            schema_name=schema_name, context=None, connection=None, create_schema=True, create_tables=True
        )

    def test_if_context_is_passed_if_provided(self, lazy_schema_cls, schema_name, context, schema_cls):
        lazy_schema_cls(schema_name, context=context).initialize()
        schema_cls.assert_called_once_with(
            schema_name=schema_name, context=context, connection=None, create_schema=True, create_tables=True
        )

    def test_if_connection_is_passed_if_provided(self, lazy_schema_cls, schema_name, connection, schema_cls):
        lazy_schema_cls(schema_name, connection=connection).initialize()
        schema_cls.assert_called_once_with(
            schema_name=schema_name, context=None, connection=connection, create_schema=True, create_tables=True
        )

    def test_if_create_schema_is_passed_if_provided(self, lazy_schema_cls, schema_name, schema_cls):
        lazy_schema_cls(schema_name, create_schema=False).initialize()
        schema_cls.assert_called_once_with(
            schema_name=schema_name, context=None, connection=None, create_schema=False, create_tables=True
        )

    def test_if_create_tables_is_passed_if_provided(self, lazy_schema_cls, schema_name, schema_cls):
        lazy_schema_cls(schema_name, create_tables=False).initialize()
        schema_cls.assert_called_once_with(
            schema_name=schema_name, context=None, connection=None, create_schema=True, create_tables=False
        )

    def test_if_schema_is_not_initialized_again_if_initialize_is_called_twice(
        self, lazy_schema_cls, schema_name, schema_cls
    ):
        lazy_schema = lazy_schema_cls(schema_name)
        lazy_schema.initialize()
        lazy_schema.initialize()
        assert schema_cls.call_count == 1


class TestGetAttr:
    @pytest.fixture
    def schema(self):
        return MagicMock(name="schema", spec=Schema, some_attribute="some_value")

    @pytest.fixture
    def schema_cls(self, schema_cls, schema):
        schema_cls.return_value = schema
        return schema_cls

    def test_if_getattr_calls_initialize_correctly(self, lazy_schema_cls, schema_name):
        lazy_schema = lazy_schema_cls(schema_name)
        initialize_mock = MagicMock(name="initialize", wraps=lazy_schema.initialize)
        lazy_schema.initialize = initialize_mock
        _ = lazy_schema.some_attribute
        initialize_mock.assert_called_once_with()

    def test_if_getattr_returns_correct_value(self, lazy_schema_cls, schema_name):
        lazy_schema = lazy_schema_cls(schema_name)
        assert lazy_schema.some_attribute == "some_value"

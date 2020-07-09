from unittest.mock import MagicMock, DEFAULT
from copy import deepcopy

import pytest


@pytest.fixture
def factory_type():
    return "source"


@pytest.fixture
def factory_args():
    return list()


@pytest.fixture
def copy_call_args():
    def _copy_call_args(mock):
        new_mock = MagicMock()

        def side_effect(*args, **kwargs):
            args = deepcopy(args)
            kwargs = deepcopy(kwargs)
            new_mock(*args, **kwargs)
            return DEFAULT

        mock.side_effect = side_effect
        return new_mock

    return _copy_call_args


def test_if_schema_is_none(factory):
    assert factory.schema is None


def test_if_table_name_is_none(factory):
    assert factory.table_name is None


@pytest.mark.usefixtures("configure")
class TestSpawnTableClass:
    def test_if_missing_classes_are_spawned(self, factory, schema, copy_call_args):
        new_mock = copy_call_args(schema.spawn_missing_classes)
        factory.spawn_table_cls()
        new_mock.assert_called_once_with(context=dict())

    def test_if_table_cls_is_returned(self, factory, spawned_table_cls):
        assert factory.spawn_table_cls() is spawned_table_cls


@pytest.mark.usefixtures("configure")
class TestCall:
    def test_if_source_table_cls_is_instantiated(self, factory, spawned_table_cls):
        factory()
        spawned_table_cls.assert_called_once_with()

    def test_if_source_table_is_returned(self, factory, spawned_table):
        assert factory() == spawned_table


def test_repr(factory):
    assert repr(factory) == "SourceTableFactory()"
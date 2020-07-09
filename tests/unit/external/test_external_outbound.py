from unittest.mock import MagicMock

import pytest
from datajoint import Lookup, Part
from datajoint.errors import LostConnectionError

from link.external.outbound import OutboundTable
from link.external.source import SourceTableFactory


@pytest.fixture
def factory_type():
    return "outbound"


@pytest.fixture
def factory_args(created_table_cls):
    return [created_table_cls]


def test_if_subclass_of_source_table_factory(factory_cls):
    assert issubclass(factory_cls, SourceTableFactory)


def test_if_table_cls_is_stored_as_instance_attribute(factory, created_table_cls):
    assert factory.table_cls is created_table_cls


@pytest.fixture
def mock_spawn_table_cls(factory, spawned_table_cls):
    factory.spawn_table_cls = MagicMock(name="OutboundTableFactory.spawn_table", return_value=spawned_table_cls)


@pytest.mark.usefixtures("mock_spawn_table_cls")
class TestCall:
    @pytest.fixture
    def mock_create_table_cls(self, factory, created_table_cls):
        factory.create_table_cls = MagicMock(name="OutboundTableFactory.create_table", return_value=created_table_cls)

    @pytest.fixture
    def outbound_table_not_already_created(self, factory, mock_spawn_table_cls):
        factory.spawn_table_cls.side_effect = KeyError

    def test_if_outbound_table_is_spawned(self, factory):
        factory()
        factory.spawn_table_cls.assert_called_once_with()

    def test_if_spawned_table_is_returned(self, factory, spawned_table):
        assert factory() == spawned_table

    @pytest.mark.usefixtures("outbound_table_not_already_created", "mock_create_table_cls")
    def test_if_outbound_table_is_created_if_not_already_created(self, factory):
        factory()
        factory.create_table_cls.assert_called_once_with()

    @pytest.mark.usefixtures("outbound_table_not_already_created", "mock_create_table_cls")
    def test_if_created_table_is_returned(self, factory, created_table):
        assert factory() == created_table

    @pytest.mark.usefixtures("outbound_table_not_already_created", "mock_create_table_cls")
    def test_if_runtime_error_is_raised_if_outbound_table_can_not_be_spawned_or_created(self, factory):
        factory.create_table_cls.side_effect = LostConnectionError
        with pytest.raises(RuntimeError):
            factory()


class TestCreateTableClass:
    @pytest.mark.usefixtures("configure")
    def test_if_name_attribute_of_outbound_table_cls_is_correctly_set(self, factory, table_name, created_table_cls):
        factory.create_table_cls()
        assert created_table_cls.__name__ == table_name + "Outbound"

    @pytest.mark.usefixtures("configure")
    def test_if_outbound_schema_is_applied_to_outbound_table_class(self, factory, schema, created_table_cls):
        factory.create_table_cls()
        schema.assert_called_once_with(created_table_cls)

    @pytest.mark.usefixtures("configure")
    def test_if_outbound_table_cls_is_returned(self, factory, created_table_cls):
        assert factory.create_table_cls() is created_table_cls


def test_repr(factory):
    assert repr(factory) == "OutboundTableFactory(outbound_created_table_cls)"


class TestOutboundTable:
    def test_if_lookup_table(self):
        assert issubclass(OutboundTable, Lookup)

    def test_if_source_table_cls_is_none(self):
        assert OutboundTable.source_table_cls is None

    def test_if_definition_is_correct(self):
        assert OutboundTable.definition.strip() == "-> self.source_table_cls"

    def test_if_deletion_requested_is_part_table(self):
        assert issubclass(OutboundTable.DeletionRequested, Part)

    def test_if_definition_of_deletion_requested_part_table_is_correct(self):
        assert OutboundTable.DeletionRequested.definition.strip() == "-> master"

    def test_if_deletion_approved_is_part_table(self):
        assert issubclass(OutboundTable.DeletionApproved, Part)

    def test_if_definition_of_deletion_approved_part_table_is_correct(self):
        assert OutboundTable.DeletionApproved.definition.strip() == "-> master"
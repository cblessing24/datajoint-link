import dataclasses
from unittest.mock import MagicMock, call

import pytest

from link.entities import entity


class TestEntity:
    def test_if_dataclass(self):
        assert dataclasses.is_dataclass(entity.Entity)

    def test_if_identifier_attribute_is_present(self):
        assert entity.Entity("identifier").identifier == "identifier"


class TestManagedEntity:
    def test_if_dataclass(self):
        assert dataclasses.is_dataclass(entity.ManagedEntity)

    def test_if_subclass_of_entity(self):
        assert issubclass(entity.ManagedEntity, entity.Entity)

    def test_if_deletion_requested_attribute_is_present(self):
        assert entity.ManagedEntity("identifier", True).deletion_requested is True


class TestSourceEntity:
    def test_if_dataclass(self):
        assert dataclasses.is_dataclass(entity.SourceEntity)

    def test_if_subclass_of_entity(self):
        assert issubclass(entity.SourceEntity, entity.Entity)


class TestOutboundEntity:
    def test_if_dataclass(self):
        assert dataclasses.is_dataclass(entity.OutboundEntity)

    def test_if_subclass_of_managed_entity(self):
        assert issubclass(entity.OutboundEntity, entity.Entity)

    def test_if_deletion_approved_attribute_is_present(self):
        assert entity.OutboundEntity("identifier", True, True).deletion_approved is True


class TestLocalEntity:
    def test_if_dataclass(self):
        assert dataclasses.is_dataclass(entity.LocalEntity)

    def test_if_subclass_of_managed_entity(self):
        assert issubclass(entity.LocalEntity, entity.Entity)


@pytest.fixture
def entities(identifiers):
    return [MagicMock(name="entity_" + identifier) for identifier in identifiers]


@pytest.fixture
def entity_cls(entities):
    return MagicMock(name="entity_cls", side_effect=entities)


@pytest.fixture
def entity_creator(gateway, entity_cls, entity_creator_cls):
    entity_creator_cls._entity_cls = entity_cls
    return entity_creator_cls(gateway)


@pytest.fixture
def calls_kwargs(identifiers):
    return [dict(identifier=identifier) for identifier in identifiers]


@pytest.fixture
def calls(calls_kwargs):
    return [call(**c) for c in calls_kwargs]


class TestEntityCreator:
    def test_if_entity_cls_is_entity(self):
        assert entity.EntityCreator._entity_cls is entity.Entity

    @pytest.fixture
    def entity_creator_cls(self):
        return entity.EntityCreator

    def test_if_gateway_is_stored_as_instance_attribute(self, gateway, entity_creator):
        assert entity_creator.gateway is gateway

    def test_if_entities_are_correctly_initialized_when_creating_entities(self, entity_cls, entity_creator, calls):
        entity_creator.create_entities()
        assert entity_cls.mock_calls == calls

    def test_if_entities_are_returned(self, entities, entity_creator):
        assert entity_creator.create_entities() == entities

    def test_repr(self, entity_creator):
        assert repr(entity_creator) == "EntityCreator(gateway)"


@pytest.fixture
def add_flags_to_calls(identifiers, calls_kwargs):
    def _add_flags_to_calls(flag_name, flagged_identifiers):
        for identifier, call_kwargs in zip(identifiers, calls_kwargs):
            call_kwargs[flag_name] = True if identifier in flagged_identifiers else False

    return _add_flags_to_calls


@pytest.fixture
def add_deletion_requested_flags_to_calls(deletion_requested_identifiers, add_flags_to_calls):
    add_flags_to_calls("deletion_requested", deletion_requested_identifiers)


class TestManagedEntityCreator:
    def test_if_entity_cls_is_managed_entity(self):
        assert entity.ManagedEntityCreator._entity_cls is entity.ManagedEntity

    def test_if_subclass_of_entity_creator(self):
        assert issubclass(entity.ManagedEntityCreator, entity.EntityCreator)

    @pytest.fixture
    def entity_creator_cls(self):
        return entity.ManagedEntityCreator

    @pytest.mark.usefixtures("add_deletion_requested_flags_to_calls")
    def test_if_entities_are_correctly_initialized_when_creating_entities(self, entity_cls, entity_creator, calls):
        entity_creator.create_entities()
        assert entity_cls.mock_calls == calls

    def test_if_entities_are_returned(self, entities, entity_creator):
        assert entity_creator.create_entities() == entities


class TestSourceEntityCreator:
    def test_if_entity_cls_is_source_entity(self):
        assert entity.SourceEntityCreator._entity_cls is entity.SourceEntity

    def test_if_subclass_of_entity_creator(self):
        assert issubclass(entity.SourceEntityCreator, entity.EntityCreator)


class TestOutboundEntityCreator:
    def test_if_entity_cls_is_outbound_entity(self):
        assert entity.OutboundEntityCreator._entity_cls is entity.OutboundEntity

    def test_if_subclass_of_managed_entity_creator(self):
        assert issubclass(entity.OutboundEntityCreator, entity.ManagedEntityCreator)

    @pytest.fixture
    def entity_creator_cls(self):
        return entity.OutboundEntityCreator

    @pytest.fixture
    def add_deletion_approved_flags_to_calls(self, deletion_approved_identifiers, add_flags_to_calls):
        add_flags_to_calls("deletion_approved", deletion_approved_identifiers)

    @pytest.mark.usefixtures("add_deletion_requested_flags_to_calls", "add_deletion_approved_flags_to_calls")
    def test_if_entities_are_correctly_initialized_when_creating_entities(self, entity_cls, entity_creator, calls):
        entity_creator.create_entities()
        assert entity_cls.mock_calls == calls

    def test_if_entities_are_returned(self, entities, entity_creator):
        assert entity_creator.create_entities() == entities


class TestLocalEntityCreator:
    def test_if_entity_cls_is_local_entity(self):
        assert entity.LocalEntityCreator._entity_cls is entity.LocalEntity

    def test_if_subclass_of_managed_entity_creator(self):
        assert issubclass(entity.LocalEntityCreator, entity.ManagedEntityCreator)

import dataclasses
from unittest.mock import MagicMock, call
from abc import ABC

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


class TestFlaggedEntity:
    def test_if_dataclass(self):
        assert dataclasses.is_dataclass(entity.FlaggedEntity)

    def test_if_subclass_of_entity(self):
        assert issubclass(entity.FlaggedEntity, entity.Entity)


@pytest.fixture
def entities(identifiers):
    return [MagicMock(name="entity_" + identifier) for identifier in identifiers]


@pytest.fixture
def entity_cls(entities):
    return MagicMock(name="entity_cls", side_effect=entities)


@pytest.fixture
def entity_creator_cls(entity_creator_base_cls, entity_cls):
    class EntityCreator(entity_creator_base_cls):
        _entity_cls = None

        @property
        def entity_cls(self):
            return self._entity_cls

    EntityCreator.__name__ = entity_creator_base_cls.__name__
    EntityCreator._entity_cls = entity_cls
    return EntityCreator


@pytest.fixture
def entity_creator(entity_creator_cls, gateway):
    return entity_creator_cls(gateway)


class TestAbstractEntityCreator:
    @pytest.fixture
    def entity_creator_cls(self, entities):
        class EntityCreator(entity.AbstractEntityCreator):
            __qualname__ = "EntityCreator"
            entity_cls = None

            def _create_entities(self):
                return entities

        return EntityCreator

    def test_if_abstract_base_class(self, entity_creator_cls):
        assert issubclass(entity_creator_cls, ABC)

    def test_if_entities_are_returned_when_created(self, entities, entity_creator):
        assert entity_creator.create_entities() == entities

    def test_repr(self, entity_creator):
        assert repr(entity_creator) == "EntityCreator()"


class TestEntityCreator:
    def test_if_entity_class_is_entity(self):
        assert entity.EntityCreator.entity_cls is entity.Entity

    @pytest.fixture
    def entity_creator_base_cls(self):
        return entity.EntityCreator

    def test_if_entities_are_correctly_initialized(self, identifiers, entity_cls, entity_creator):
        entity_creator.create_entities()
        assert entity_cls.mock_calls == [call(identifier) for identifier in identifiers]

    def test_if_entities_are_returned(self, entities, entity_creator):
        assert entity_creator.create_entities() == entities


class TestFlaggedEntityCreator:
    def test_if_entity_class_is_flagged_entity(self):
        assert entity.FlaggedEntityCreator.entity_cls is entity.FlaggedEntity

    @pytest.fixture
    def entity_creator_base_cls(self):
        return entity.FlaggedEntityCreator

    @pytest.fixture
    def deletion_requested_flags(self, n_identifiers, deletion_requested_indexes):
        return [True if i in deletion_requested_indexes else False for i in range(n_identifiers)]

    @pytest.fixture
    def deletion_approved_flags(self, n_identifiers, deletion_approved_indexes):
        return [True if i in deletion_approved_indexes else False for i in range(n_identifiers)]

    def test_if_entities_are_correctly_initialized(
        self, identifiers, entity_cls, entity_creator, deletion_requested_flags, deletion_approved_flags
    ):
        entity_creator.create_entities()
        calls = []
        for identifier, deletion_requested_flag, deletion_approved_flag in zip(
            identifiers, deletion_requested_flags, deletion_approved_flags
        ):
            calls.append(call(identifier, deletion_requested_flag, deletion_approved_flag))
        assert entity_cls.mock_calls == calls

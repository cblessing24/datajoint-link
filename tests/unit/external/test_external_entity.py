from dataclasses import is_dataclass

from link.external.entity import Entity


def test_if_table_entity_is_dataclass():
    assert is_dataclass(Entity)
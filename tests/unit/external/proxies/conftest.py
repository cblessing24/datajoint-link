from unittest.mock import MagicMock
from string import ascii_uppercase

import pytest

from link.external.proxies import TableEntity


@pytest.fixture
def primary_attr_names():
    return ["pa0", "pa1", "pa2"]


@pytest.fixture
def n_entities():
    return 3


@pytest.fixture
def primary_keys(n_entities):
    return ["pk" + str(i) for i in range(n_entities)]


@pytest.fixture
def master_entities(n_entities):
    return ["Main_entity" + str(i) for i in range(n_entities)]


@pytest.fixture
def n_parts():
    return 4


@pytest.fixture
def part_names(n_parts):
    return ["Part" + ascii_uppercase[i] for i in range(n_parts)]


@pytest.fixture
def part_entities(n_entities, part_names):
    return {name: [name + "_entities" + str(i) for i in range(n_entities)] for name in part_names}


@pytest.fixture
def table_entities(master_entities, part_entities):
    table_entities = [
        TableEntity(master=master_entity, parts={name: entities[i] for name, entities in part_entities.items()})
        for i, master_entity in enumerate(master_entities)
    ]
    return table_entities


@pytest.fixture
def parts(part_entities):
    parts = dict()
    for name, entities in part_entities.items():
        part = MagicMock(name=name)
        part.__and__.return_value.fetch.side_effect = entities
        parts[name] = part
    return parts


@pytest.fixture
def table(primary_attr_names, primary_keys, master_entities):
    table = MagicMock(name="table")
    table.heading.primary_key = primary_attr_names
    table.proj.return_value.fetch.return_value = primary_keys
    table.proj.return_value.__and__.return_value.fetch.return_value = primary_keys
    table.__and__.return_value.fetch1.side_effect = master_entities
    table.DeletionRequested.fetch.return_value = primary_keys
    table.DeletionApproved.fetch.return_value = primary_keys
    return table


@pytest.fixture
def table_factory(primary_attr_names, parts, table):
    name = "table_factory"
    table_factory = MagicMock(name=name, return_value=table)
    table_factory.parts = parts
    table_factory.__repr__ = MagicMock(name=name + ".__repr__", return_value=name)
    return table_factory


@pytest.fixture
def download_path():
    return "download_path"


@pytest.fixture
def proxy(proxy_cls, table_factory, download_path):
    return proxy_cls(table_factory, download_path)

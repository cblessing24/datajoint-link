from typing import List, Dict, Union, Any


PrimaryKey = Dict[str, Union[str, int, float]]


class SourceTableProxy:
    def __init__(self, table_factory):
        self.table_factory = table_factory

    @property
    def primary_attr_names(self) -> List[str]:
        return self.table_factory.heading.primary_key

    @property
    def primary_keys(self) -> List[PrimaryKey]:
        return self.table_factory().proj().fetch(as_dict=True)

    def get_primary_keys_in_restriction(self, restriction) -> List[PrimaryKey]:
        return (self.table_factory().proj() & restriction).fetch(as_dict=True)

    def fetch(self, primary_keys: List[PrimaryKey]) -> Dict[str, Any]:
        entities = dict(main=(self.table_factory() & primary_keys).fetch(as_dict=True))
        entities["parts"] = dict()
        for name, part in self.table_factory.parts.items():
            entities["parts"][name] = (part & primary_keys).fetch(as_dict=True)
        return entities

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + "(" + repr(self.table_factory) + ")"


class NonSourceTableProxy(SourceTableProxy):
    @property
    def deletion_requested(self) -> List[PrimaryKey]:
        return self.table_factory().DeletionRequested.fetch(as_dict=True)

    def delete(self, primary_keys: List[PrimaryKey]) -> None:
        (self.table_factory() & primary_keys).delete()

    def insert(self, entities: Dict[str, Any]) -> None:
        self.table_factory().insert(entities["main"])
        for part_name, part_entities in entities["parts"].items():
            self.table_factory.parts[part_name].insert(part_entities)

    def start_transaction(self) -> None:
        self.table_factory().connection.start_transaction()

    def commit_transaction(self) -> None:
        self.table_factory().connection.commit_transaction()

    def cancel_transaction(self) -> None:
        self.table_factory().connection.cancel_transaction()


class OutboundTableProxy(NonSourceTableProxy):
    @property
    def deletion_approved(self) -> List[PrimaryKey]:
        return self.table_factory().DeletionApproved.fetch(as_dict=True)

    def approve_deletion(self, primary_keys: List[PrimaryKey]) -> None:
        self.table_factory().DeletionApproved.insert(primary_keys)


class LocalTableProxy(NonSourceTableProxy):
    pass

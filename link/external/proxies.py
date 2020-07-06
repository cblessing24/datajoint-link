from typing import List, Dict, Union, Any


PrimaryKey = Dict[str, Union[str, int, float]]


class ReadOnlyTableProxy:
    def __init__(self, table):
        self.table = table

    @property
    def primary_attr_names(self) -> List[str]:
        return self.table.heading.primary_key

    @property
    def primary_keys(self) -> List[PrimaryKey]:
        return self.table.proj().fetch(as_dict=True)

    def fetch(self, primary_keys: List[PrimaryKey]) -> Dict[str, Any]:
        return (self.table & primary_keys).fetch(as_dict=True)

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + "(" + repr(self.table) + ")"


class TableProxy(ReadOnlyTableProxy):
    @property
    def deletion_requested(self) -> List[PrimaryKey]:
        return self.table.DeletionRequested.fetch(as_dict=True)

    @property
    def deletion_approved(self) -> List[PrimaryKey]:
        return self.table.DeletionApproved.fetch(as_dict=True)

    def delete(self, primary_keys: List[PrimaryKey]) -> None:
        (self.table & primary_keys).delete()

    def insert(self, entities: Dict[str, Any]) -> None:
        self.table.insert(entities)

    def start_transaction(self) -> None:
        self.table.connection.start_transaction()

    def commit_transaction(self) -> None:
        self.table.connection.commit_transaction()

    def cancel_transaction(self) -> None:
        self.table.connection.cancel_transaction()


class SourceTableProxy(ReadOnlyTableProxy):
    pass


class OutboundTableProxy(TableProxy):
    def approve_deletion(self, primary_keys: List[PrimaryKey]) -> None:
        self.table.DeletionApproved.insert(primary_keys)


class LocalTableProxy(TableProxy):
    pass
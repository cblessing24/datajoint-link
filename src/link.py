from contextlib import contextmanager

from datajoint import Lookup
from datajoint.schemas import Schema
from datajoint.connection import Connection, conn


class LinkedSchema(Schema):
    def __init__(self, host, schema_name, user="datajoint", password="datajoint"):
        connection = Connection(host, user, password)
        super().__init__(schema_name, connection=connection)


class Link:
    def __init__(self, source_schema, linked_schema):
        self.source_schema = source_schema
        self.linked_schema = linked_schema
        self.source_conn = Connection(source_schema.connection.conn_info["host"], "datajoint", "datajoint")
        self.link_conn = linked_schema.connection
        self.source_table = None
        self.outbound_table = None
        self.linked_table = None

    def __call__(self, table_cls):
        self.create_source_table(table_cls)
        self.create_outbound_table(table_cls)
        self.create_linked_table(table_cls)
        return self.source_table

    def create_source_table(self, table_cls):
        class SourceTable(table_cls):
            link = self

            def sync(self):
                self.link.sync()

            def delete(self):
                self.link.delete(self.restriction)

        SourceTable.__name__ = table_cls.__name__
        self.source_table = self.source_schema(SourceTable)

    def create_outbound_table(self, table_cls):
        class OutboundTable(Lookup):
            source_table = self.source_table

            definition = """
            host: varchar(64)
            schema_name: varchar(64)
            -> self.source_table
            """

        OutboundTable.__name__ = table_cls.__name__ + "Outbound"
        outbound_schema = Schema("datajoint_outbound__" + self.source_schema.database, connection=self.source_conn)
        self.outbound_table = outbound_schema(OutboundTable)

    def create_linked_table(self, table_cls):
        class ExternalTable(table_cls):
            pass

        ExternalTable.__name__ = table_cls.__name__
        with self.connection(self.link_conn):
            self.linked_table = self.linked_schema(ExternalTable)

    def sync(self):
        self.refresh()
        host = self.linked_schema.connection.conn_info["host"]
        schema_name = self.linked_schema.database
        with self.connection(self.source_conn):
            primary_keys = (self.source_table.proj() - self.outbound_table).fetch(as_dict=True)
            entities = (self.source_table - self.outbound_table).fetch()
        try:
            with self.connection(self.source_conn) as source_conn:
                source_conn.start_transaction()
                self.outbound_table.insert([dict(host=host, schema_name=schema_name, **pk) for pk in primary_keys])
            with self.connection(self.link_conn) as link_conn:
                link_conn.start_transaction()
                self.linked_table.insert(entities)
        except Exception:
            source_conn.cancel_transaction()
            link_conn.cancel_transaction()
            raise
        finally:
            source_conn.commit_transaction()
            link_conn.commit_transaction()

    def refresh(self):
        with self.connection(self.link_conn):
            primary_keys = self.linked_table.proj().fetch()
        with self.connection(self.source_conn) as source_conn:
            with source_conn.transaction:
                (self.outbound_table - primary_keys).delete_quick()

    def delete(self, restriction):
        self.refresh()
        (self.source_table & restriction).delete_quick()

    @contextmanager
    def connection(self, connection):
        old_table_conn = self.source_table.connection
        if hasattr(conn, "connection"):
            old_conn = conn.connection
        else:
            old_conn = None
        conn.connection = connection
        if connection is self.source_conn:
            self.source_table.connection = connection
        try:
            yield connection
        finally:
            if old_conn:
                conn.connection = old_conn
            else:
                delattr(conn, "connection")
            self.source_table.connection = old_table_conn

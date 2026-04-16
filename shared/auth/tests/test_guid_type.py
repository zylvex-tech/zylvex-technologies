import uuid

from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable

from app.models.types import GUID


def test_guid_uses_sqlite_compatible_type():
    metadata = MetaData()
    table = Table("guid_test", metadata, Column("id", GUID(), primary_key=True))

    create_sql = str(CreateTable(table).compile(dialect=sqlite.dialect()))
    assert "CHAR(36)" in create_sql

    engine = create_engine("sqlite://")
    metadata.create_all(bind=engine)


def test_guid_bind_and_result_conversion():
    value = uuid.uuid4()
    guid = GUID()

    assert guid.process_bind_param(value, sqlite.dialect()) == str(value)
    assert guid.process_bind_param(str(value), sqlite.dialect()) == str(value)
    assert guid.process_bind_param(value, postgresql.dialect()) == value

    assert guid.process_result_value(str(value), sqlite.dialect()) == value
    assert guid.process_result_value(value, postgresql.dialect()) == value

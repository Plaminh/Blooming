"""Fresh-install parity checks for the SQL baseline and SQLAlchemy metadata."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import pytest
from sqlalchemy import inspect
from sqlalchemy.schema import ForeignKeyConstraint, Index

# Import through the application package, not individual model modules. This verifies
# that app.db.models registers the complete application model set on Base.metadata.
from app.db import Base, models  # noqa: F401


EXPECTED_TABLE_COUNT = 24


def _type_signature(column_type: Any, dialect: Any) -> str:
    """Return the database spelling relevant to persisted type compatibility."""

    return re.sub(r"\s+", " ", column_type.compile(dialect=dialect).upper()).strip()


def _normalize_sql(value: Any, table_name: str) -> str | None:
    if value is None:
        return None
    normalized = str(value).lower().replace('"', "")
    normalized = re.sub(rf"\b{re.escape(table_name.lower())}\.", "", normalized)
    normalized = normalized.replace("::text", "")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    while normalized.startswith("(") and normalized.endswith(")"):
        normalized = normalized[1:-1].strip()
    return normalized


def _reflected_indexes(inspector: Any, table_name: str) -> dict[str, dict[str, Any]]:
    indexes: dict[str, dict[str, Any]] = {}
    for index in inspector.get_indexes(table_name):
        # PostgreSQL exposes the physical index behind UNIQUE constraints here too.
        # SQLAlchemy represents those as UniqueConstraint, not Index.
        if index.get("duplicates_constraint"):
            continue
        expressions = index.get("expressions") or index.get("column_names") or []
        column_sorting = index.get("column_sorting") or {}
        normalized_expressions = []
        for expression in expressions:
            normalized = _normalize_sql(expression, table_name)
            sorting = column_sorting.get(expression) or ()
            if "desc" in sorting:
                normalized = f"{normalized} desc"
            normalized_expressions.append(normalized)
        options = index.get("dialect_options") or {}
        indexes[index["name"]] = {
            "unique": bool(index.get("unique")),
            "expressions": tuple(normalized_expressions),
            # PostgreSQL rewrites predicates during storage (for example IN into
            # ANY plus casts). Presence is stable across that normalization.
            "partial": options.get("postgresql_where") is not None,
        }
    return indexes


def _metadata_indexes(
    indexes: Iterable[Index], table_name: str
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index in indexes:
        where = index.dialect_options["postgresql"].get("where")
        result[index.name] = {
            "unique": bool(index.unique),
            "expressions": tuple(
                _normalize_sql(expression, table_name)
                for expression in index.expressions
            ),
            "partial": where is not None,
        }
    return result


def _reflected_foreign_keys(
    inspector: Any, table_name: str
) -> set[tuple[tuple[str, ...], str, tuple[str, ...], str | None]]:
    result = set()
    for foreign_key in inspector.get_foreign_keys(table_name):
        options = foreign_key.get("options") or {}
        result.add(
            (
                tuple(foreign_key["constrained_columns"]),
                foreign_key["referred_table"],
                tuple(foreign_key["referred_columns"]),
                options.get("ondelete") or None,
            )
        )
    return result


def _metadata_foreign_keys(
    constraints: Iterable[Any],
) -> set[tuple[tuple[str, ...], str, tuple[str, ...], str | None]]:
    result = set()
    for constraint in constraints:
        if not isinstance(constraint, ForeignKeyConstraint):
            continue
        elements = tuple(constraint.elements)
        result.add(
            (
                tuple(element.parent.name for element in elements),
                elements[0].column.table.name,
                tuple(element.column.name for element in elements),
                constraint.ondelete or None,
            )
        )
    return result


@pytest.mark.asyncio
async def test_fresh_sql_install_matches_registered_orm_metadata(db_session):
    """Compare a database installed from install.sql with application metadata."""

    def inspect_parity(connection):
        inspector = inspect(connection)
        sql_tables = set(inspector.get_table_names(schema="public"))
        orm_tables = set(Base.metadata.tables)
        differences: list[str] = []

        if len(sql_tables) != EXPECTED_TABLE_COUNT:
            differences.append(
                f"SQL table count: expected {EXPECTED_TABLE_COUNT}, got {len(sql_tables)}"
            )
        if len(orm_tables) != EXPECTED_TABLE_COUNT:
            differences.append(
                f"ORM table count: expected {EXPECTED_TABLE_COUNT}, got {len(orm_tables)}"
            )

        for table_name in sorted(sql_tables - orm_tables):
            differences.append(f"unexpected SQL table: {table_name}")
        for table_name in sorted(orm_tables - sql_tables):
            differences.append(f"missing SQL table: {table_name}")

        for table_name in sorted(sql_tables & orm_tables):
            orm_table = Base.metadata.tables[table_name]
            sql_columns = {
                column["name"]: column
                for column in inspector.get_columns(table_name, schema="public")
            }
            orm_columns = {column.name: column for column in orm_table.columns}

            for column_name in sorted(sql_columns.keys() - orm_columns.keys()):
                differences.append(f"missing ORM column: {table_name}.{column_name}")
            for column_name in sorted(orm_columns.keys() - sql_columns.keys()):
                differences.append(f"missing SQL column: {table_name}.{column_name}")

            for column_name in sorted(sql_columns.keys() & orm_columns.keys()):
                sql_column = sql_columns[column_name]
                orm_column = orm_columns[column_name]
                sql_type = _type_signature(sql_column["type"], connection.dialect)
                orm_type = _type_signature(orm_column.type, connection.dialect)
                if sql_type != orm_type:
                    differences.append(
                        f"type mismatch: {table_name}.{column_name}: "
                        f"SQL={sql_type}, ORM={orm_type}"
                    )
                if sql_column["nullable"] != orm_column.nullable:
                    differences.append(
                        f"nullable mismatch: {table_name}.{column_name}: "
                        f"SQL={sql_column['nullable']}, ORM={orm_column.nullable}"
                    )

            sql_pk = tuple(
                inspector.get_pk_constraint(table_name, schema="public").get(
                    "constrained_columns"
                )
                or ()
            )
            orm_pk = tuple(column.name for column in orm_table.primary_key.columns)
            if sql_pk != orm_pk:
                differences.append(
                    f"primary key mismatch: {table_name}: SQL={sql_pk}, ORM={orm_pk}"
                )

            sql_fks = _reflected_foreign_keys(inspector, table_name)
            orm_fks = _metadata_foreign_keys(orm_table.constraints)
            if sql_fks != orm_fks:
                differences.append(
                    f"foreign key mismatch: {table_name}: "
                    f"SQL={sorted(sql_fks)}, ORM={sorted(orm_fks)}"
                )

            sql_indexes = _reflected_indexes(inspector, table_name)
            orm_indexes = _metadata_indexes(orm_table.indexes, table_name)
            for index_name in sorted(sql_indexes.keys() - orm_indexes.keys()):
                differences.append(f"missing ORM index: {table_name}.{index_name}")
            for index_name in sorted(orm_indexes.keys() - sql_indexes.keys()):
                differences.append(f"missing SQL index: {table_name}.{index_name}")
            for index_name in sorted(sql_indexes.keys() & orm_indexes.keys()):
                if sql_indexes[index_name] != orm_indexes[index_name]:
                    differences.append(
                        f"index mismatch: {table_name}.{index_name}: "
                        f"SQL={sql_indexes[index_name]}, ORM={orm_indexes[index_name]}"
                    )

        assert not differences, "SQL/ORM parity differences:\n- " + "\n- ".join(
            differences
        )

    connection = await db_session.connection()
    await connection.run_sync(inspect_parity)

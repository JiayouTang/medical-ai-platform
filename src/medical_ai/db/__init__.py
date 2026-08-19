"""Database schema and executors."""

from medical_ai.db.schema import public_schema

__all__ = ["MySQLExecutor", "QueryExecutor", "QueryResult", "public_schema"]


def __getattr__(name: str):
    if name in {"MySQLExecutor", "QueryExecutor", "QueryResult"}:
        from medical_ai.db import executor

        return getattr(executor, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

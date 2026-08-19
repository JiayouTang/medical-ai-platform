from typing import Any

from medical_ai.config import get_settings
from medical_ai.db import MySQLExecutor, public_schema
from medical_ai.query import QueryValidationError, compile_query, validate_query_spec


def get_database_schema() -> dict[str, Any]:
    """Return the allowlisted database schema exposed to agents."""

    return public_schema()


def get_distinct_values(table: str, field: str, limit: int = 100) -> dict[str, Any]:
    """Return distinct values for an allowlisted table field."""

    settings = get_settings()
    effective_limit = min(max(limit, 1), settings.query_max_distinct_values)
    result = MySQLExecutor(settings=settings).fetch_distinct_values(table, field, effective_limit)
    values = [row[field] for row in result.rows]
    return {
        "table": table,
        "field": field,
        "values": values,
        "row_count": len(values),
        "truncated": result.truncated,
        "query_time_ms": result.query_time_ms,
        "metadata": result.metadata,
    }


def query_medical_data(query_spec: dict[str, Any]) -> dict[str, Any]:
    """Validate QuerySpec JSON, compile it to safe SQL, execute it, and return JSON data."""

    spec = validate_query_spec(query_spec)
    query = compile_query(spec)
    result = MySQLExecutor().execute(query)
    return result.to_dict()


def validate_query_spec_only(query_spec: dict[str, Any]) -> dict[str, Any]:
    """Helper for direct tests and future debugging; not registered as an MCP tool."""

    try:
        spec = validate_query_spec(query_spec)
    except QueryValidationError as exc:
        return {"valid": False, "error": str(exc)}
    return {"valid": True, "query_spec": spec.model_dump(mode="json")}

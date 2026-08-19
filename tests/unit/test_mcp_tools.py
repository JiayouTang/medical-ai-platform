import asyncio

from medical_ai.mcp_server.server import mcp
from medical_ai.mcp_server.tools import get_database_schema, validate_query_spec_only


def test_get_database_schema_is_available_without_database() -> None:
    schema = get_database_schema()
    table = schema["tables"][0]

    assert table["name"] == "inpatient"
    assert any(column["name"] == "TotalCharges" for column in table["columns"])


def test_validate_query_spec_only_reports_invalid_query_without_database() -> None:
    result = validate_query_spec_only(
        {
            "table": "inpatient",
            "filters": [{"field": "NotAField", "op": "=", "value": 1}],
            "limit": 10,
        }
    )

    assert result["valid"] is False
    assert "NotAField" in result["error"]


def test_mcp_server_registers_expected_tools() -> None:
    tool_names = {tool.name for tool in asyncio.run(mcp.list_tools())}

    assert {"get_database_schema", "get_distinct_values", "query_medical_data"}.issubset(tool_names)

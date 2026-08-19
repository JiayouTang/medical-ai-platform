#!/usr/bin/env python
import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


DEFAULT_QUERY_SPEC = {
    "table": "inpatient",
    "filters": [
        {"field": "DischargeYear", "op": "=", "value": 2021},
        {"field": "AgeGroup", "op": "in", "value": ["50to69", "70orOlder"]},
    ],
    "group_by": ["AgeGroup"],
    "metrics": [
        {"field": "TotalCharges", "agg": "avg", "alias": "avg_total_charges"},
        {"field": "*", "agg": "count", "alias": "patient_count"},
    ],
    "order_by": [{"field": "avg_total_charges", "direction": "desc"}],
    "limit": 100,
}


async def run(url: str, query_spec_path: Path | None) -> dict[str, Any]:
    query_spec = DEFAULT_QUERY_SPEC
    if query_spec_path is not None:
        query_spec = json.loads(query_spec_path.read_text(encoding="utf-8"))

    async with streamable_http_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            schema = await session.call_tool("get_database_schema", arguments={})
            distinct = await session.call_tool(
                "get_distinct_values",
                arguments={"table": "inpatient", "field": "AgeGroup", "limit": 10},
            )
            query_result = await session.call_tool(
                "query_medical_data",
                arguments={"query_spec": query_spec},
            )

    return {
        "tools": [tool.name for tool in tools.tools],
        "schema_table_count": len(_tool_result_payload(schema).get("tables", [])),
        "distinct_age_group": _tool_result_payload(distinct),
        "query_result": _tool_result_payload(query_result),
    }


def _tool_result_payload(result: Any) -> Any:
    if getattr(result, "structured_content", None) is not None:
        return result.structured_content
    content = getattr(result, "content", None) or []
    if len(content) == 1 and isinstance(content[0], TextContent):
        try:
            return json.loads(content[0].text)
        except json.JSONDecodeError:
            return content[0].text
    return [item.model_dump(mode="json") for item in content]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the medical MCP server through Streamable HTTP.")
    parser.add_argument("--url", default="http://127.0.0.1:3001/mcp")
    parser.add_argument("--query-spec", type=Path, default=None)
    args = parser.parse_args()

    print(json.dumps(asyncio.run(run(args.url, args.query_spec)), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

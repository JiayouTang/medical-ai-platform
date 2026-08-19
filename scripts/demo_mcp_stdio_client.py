#!/usr/bin/env python
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
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


async def run(query_spec_path: Path | None) -> dict[str, Any]:
    env = dict(os.environ)
    env["MCP_TRANSPORT"] = "stdio"
    env["PYTHONPATH"] = str(SRC)
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "medical_ai.mcp_server.server"],
        env=env,
        cwd=ROOT,
    )
    query_spec = DEFAULT_QUERY_SPEC
    if query_spec_path is not None:
        query_spec = json.loads(query_spec_path.read_text(encoding="utf-8"))

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("mcp: initialize", file=sys.stderr)
            await asyncio.wait_for(session.initialize(), timeout=10)
            print("mcp: list_tools", file=sys.stderr)
            tools = await asyncio.wait_for(session.list_tools(), timeout=10)
            print("mcp: get_database_schema", file=sys.stderr)
            schema = await asyncio.wait_for(session.call_tool("get_database_schema", arguments={}), timeout=10)
            print("mcp: get_distinct_values", file=sys.stderr)
            distinct = await asyncio.wait_for(
                session.call_tool(
                "get_distinct_values",
                arguments={"table": "inpatient", "field": "AgeGroup", "limit": 10},
                ),
                timeout=10,
            )
            print("mcp: query_medical_data", file=sys.stderr)
            query_result = await asyncio.wait_for(
                session.call_tool(
                "query_medical_data",
                arguments={"query_spec": query_spec},
                ),
                timeout=10,
            )

    return {
        "tools": [tool.name for tool in tools.tools],
        "schema": _tool_result_payload(schema),
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
    parser = argparse.ArgumentParser(description="Validate the medical MCP server through real stdio transport.")
    parser.add_argument("--query-spec", type=Path, default=None)
    args = parser.parse_args()

    print(json.dumps(asyncio.run(run(args.query_spec)), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

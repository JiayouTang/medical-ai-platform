#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_ai.agent import QueryPlanner
from medical_ai.db import MySQLExecutor
from medical_ai.query import compile_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Use configured LLM to produce QuerySpec and optionally execute it.")
    parser.add_argument("question")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    planned = QueryPlanner().plan(args.question)
    query = compile_query(planned.query_spec)
    output = {
        "question": planned.question,
        "query_spec": planned.query_spec.model_dump(mode="json"),
        "compiled_sql": query.sql,
        "compiled_params": query.params,
    }
    if args.execute:
        output["result"] = MySQLExecutor().execute(query).to_dict()

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

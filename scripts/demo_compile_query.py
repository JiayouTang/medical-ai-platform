#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_ai.query import compile_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile QuerySpec JSON to safe parameterized MySQL SQL.")
    parser.add_argument("queryspec", type=Path)
    args = parser.parse_args()

    with args.queryspec.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    query = compile_query(data)
    print(
        json.dumps(
            {
                "sql": query.sql,
                "params": query.params,
                "table": query.table,
                "limit": query.limit,
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


if __name__ == "__main__":
    main()

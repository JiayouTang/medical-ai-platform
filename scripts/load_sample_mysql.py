#!/usr/bin/env python
import argparse
import csv
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_ai.db import MySQLExecutor
from medical_ai.db.schema import build_sqlalchemy_table

INTEGER_FIELDS = {"LengthOfStay", "DischargeYear", "APRDRGCode", "APRSeverityOfIllnessCode"}
DECIMAL_FIELDS = {"TotalCharges", "TotalCosts"}


def cast_row(row: dict[str, str]) -> dict[str, Any]:
    casted: dict[str, Any] = {}
    for key, value in row.items():
        if value == "":
            casted[key] = None
        elif key in INTEGER_FIELDS:
            casted[key] = int(value)
        elif key in DECIMAL_FIELDS:
            casted[key] = Decimal(value)
        else:
            casted[key] = value
    return casted


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [cast_row(row) for row in csv.DictReader(handle)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load synthetic development sample data into MySQL.")
    parser.add_argument("--csv", type=Path, default=ROOT / "data" / "sample" / "inpatient_sample.csv")
    parser.add_argument("--replace", action="store_true", help="Delete existing rows from inpatient before loading.")
    args = parser.parse_args()

    rows = read_rows(args.csv)
    metadata = MetaData()
    table = build_sqlalchemy_table("inpatient", metadata)
    executor = MySQLExecutor()

    metadata.create_all(executor.engine, tables=[table])
    with executor.engine.begin() as connection:
        if args.replace:
            connection.execute(table.delete())
        connection.execute(table.insert(), rows)

    print(f"Loaded {len(rows)} synthetic development rows into inpatient.")


if __name__ == "__main__":
    main()

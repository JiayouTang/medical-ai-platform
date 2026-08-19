#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_ai.agent import MedicalDataAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LLM-first medical data agent.")
    parser.add_argument("question")
    parser.add_argument("--no-execute", action="store_true", help="Only plan; do not query MySQL.")
    parser.add_argument("--no-interpret", action="store_true", help="Skip the result interpretation LLM call.")
    args = parser.parse_args()

    run = MedicalDataAgent().run(
        args.question,
        execute=not args.no_execute,
        interpret=not args.no_interpret,
    )
    print(json.dumps(run.to_dict(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

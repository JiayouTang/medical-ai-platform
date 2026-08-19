#!/usr/bin/env python
import argparse
import json
import mimetypes
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FRONTEND = ROOT / "frontend"
STATIC_ROOT = FRONTEND / "dist" if (FRONTEND / "dist").exists() else FRONTEND
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_ai.agent import MedicalDataAgent
from medical_ai.config import get_settings
from medical_ai.db import MySQLExecutor
from medical_ai.mcp_server.tools import get_database_schema, get_distinct_values, query_medical_data
from medical_ai.query import compile_query


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "MedicalAIDemo/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json(HTTPStatus.OK, health_payload())
            return
        if parsed.path == "/api/schema":
            self._json(HTTPStatus.OK, get_database_schema())
            return
        if parsed.path == "/api/distinct":
            params = parse_qs(parsed.query)
            table = _first(params, "table", "inpatient")
            field = _first(params, "field", "AgeGroup")
            limit = int(_first(params, "limit", "50"))
            self._json(HTTPStatus.OK, get_distinct_values(table=table, field=field, limit=limit))
            return
        self._static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/api/query":
                result = query_medical_data(payload.get("query_spec", payload))
                self._json(HTTPStatus.OK, {"result": result})
                return
            if parsed.path == "/api/ask":
                question = str(payload.get("question") or "").strip()
                if not question:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "question is required"})
                    return
                execute = bool(payload.get("execute", True))
                self._json(HTTPStatus.OK, ask_payload(question, execute=execute))
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": f"Unknown API route: {parsed.path}"})
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors_headers()
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}", file=sys.stderr)

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > 2_000_000:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, request_path: str) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        path = (STATIC_ROOT / relative).resolve()
        static_root = STATIC_ROOT.resolve()
        if static_root not in path.parents and path != static_root:
            self._json(HTTPStatus.FORBIDDEN, {"error": "Forbidden"})
            return
        if not path.exists() or path.is_dir():
            path = STATIC_ROOT / "index.html"
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self._cors_headers()
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def health_payload() -> dict[str, Any]:
    settings = get_settings()
    executor = MySQLExecutor(settings=settings)
    start = time.perf_counter()
    query = compile_query(
        {
            "table": "inpatient",
            "metrics": [{"field": "*", "agg": "count", "alias": "row_count"}],
            "limit": 1,
        }
    )
    result = executor.execute(query)
    return {
        "ok": True,
        "database": settings.mysql_database,
        "row_count": result.rows[0]["row_count"] if result.rows else 0,
        "llm_configured": bool(settings.llm_base_url and settings.llm_api_key and settings.llm_model),
        "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
    }


def ask_payload(question: str, execute: bool) -> dict[str, Any]:
    return MedicalDataAgent().run(question, execute=execute, interpret=execute).to_dict()


def _first(params: dict[str, list[str]], key: str, default: str) -> str:
    values = params.get(key)
    return values[0] if values else default


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local HTTP demo server for the medical AI platform.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    print(f"Demo server running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

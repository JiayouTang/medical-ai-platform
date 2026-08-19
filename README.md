# Smart Medical Big Data and AI Analysis Platform

This repository is the phase-1 MVP skeleton for a hospital inpatient discharge data analysis platform.

The current scope is intentionally narrow:

```text
QuerySpec JSON
  -> validation
  -> safe SQLAlchemy Core query compilation
  -> MySQL executor
  -> structured JSON result
  -> MCP tools
```

The current working loop also includes an OpenAI-compatible LLM-first Agent that returns intent, safe `QuerySpec`, chart recommendation, execution steps, and a short result interpretation. A React/MUI/ECharts demo frontend renders the result table, chart, and Agent insight. Spark/Hadoop and Python code execution are reserved for later phases.

## Project Root

The formal project lives in `medical-ai-platform/` because the parent workspace already contains design documents, raw data, and a read-only `.git/` directory that cannot be initialized safely.

## Environment

Conda owns the Python runtime. `pyproject.toml` owns Python package dependencies.

```bash
conda env create -f environment.yml
conda activate medical-ai
```

For an existing environment:

```bash
conda activate medical-ai
pip install -e ".[dev]"
```

## Configuration

```bash
cp .env.example .env
```

Edit `.env` locally. Never commit `.env`.

## MySQL

Docker is optional. The current WSL environment uses local MySQL installed through Ubuntu packages.

Local MySQL route:

```bash
sudo apt-get update
sudo apt-get install -y mysql-server mysql-client
sudo service mysql start
```

Create database and project user from `.env`:

```bash
set -a
source .env
set +a
sudo mysql -e "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci; CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}'; CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASSWORD}'; GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'localhost'; GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'127.0.0.1'; FLUSH PRIVILEGES;"
```

The local development password is stored only in `.env` as `MYSQL_PASSWORD`. Do not commit `.env`.

Docker route, if Docker is available later:

```bash
docker compose --env-file .env -f infra/docker-compose.yml up -d mysql
```

Load synthetic development data:

```bash
conda run -n medical-ai python scripts/load_sample_mysql.py --replace
```

Clean and load a 1000-row development subset from the real SPARCS CSV:

```bash
conda run -n medical-ai python scripts/clean_sparcs_csv.py --limit 1000 --output data/processed/inpatient_sparcs_2021_clean_1000.csv
conda run -n medical-ai python scripts/load_sparcs_mysql.py --csv data/processed/inpatient_sparcs_2021_clean_1000.csv --replace-table
```

For the full SPARCS file, omit `--limit`. `data/processed/*` is ignored by Git.

Fast full-load path:

```bash
sudo mysql -e "SET GLOBAL local_infile = 1; SHOW GLOBAL VARIABLES LIKE 'local_infile';"
conda run -n medical-ai python scripts/load_sparcs_mysql.py --csv data/processed/inpatient_sparcs_2021_clean.csv --replace-table --method load-data
```

If `local_infile` cannot be enabled, use the slower batch-insert path:

```bash
conda run -n medical-ai python scripts/load_sparcs_mysql.py --csv data/processed/inpatient_sparcs_2021_clean.csv --replace-table --method insert
```

Verify:

```bash
RUN_MYSQL_TESTS=1 conda run -n medical-ai pytest tests/integration
conda run -n medical-ai python scripts/demo_query_mysql.py data/sample/queryspec_avg_charges_by_age.json
```

## Tests

```bash
pytest
```

Optional MySQL integration tests:

```bash
RUN_MYSQL_TESTS=1 pytest tests/integration
```

## Minimal Demo

Compile QuerySpec JSON to safe parameterized MySQL SQL without a database:

```bash
python scripts/demo_compile_query.py data/sample/queryspec_avg_charges_by_age.json
```

Execute against configured MySQL:

```bash
python scripts/demo_query_mysql.py data/sample/queryspec_avg_charges_by_age.json
```

Use the configured OpenAI-compatible LLM to plan and execute a query:

```bash
conda run -n medical-ai python scripts/demo_llm_query.py "2021年50到69岁和70岁以上患者的平均总费用是多少，按年龄组排序" --execute
```

Run the LLM-first Agent path with intent, chart recommendation, MySQL execution, and result interpretation:

```bash
conda run -n medical-ai python scripts/demo_agent_query.py "2021年50到69岁和70岁以上患者的平均总费用是多少，按年龄组排序"
```

Required local `.env` values:

```text
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

## MCP Server

Default stdio transport:

```bash
python -m medical_ai.mcp_server.server
```

Streamable HTTP transport:

```bash
MCP_TRANSPORT=streamable-http MCP_PORT=3001 python -m medical_ai.mcp_server.server
```

Available tools:

- `get_database_schema`
- `get_distinct_values`
- `query_medical_data`

Validated Streamable HTTP client demo:

```bash
conda run -n medical-ai python scripts/demo_mcp_http_client.py --url http://127.0.0.1:3001/mcp
```

## Frontend Demo

The demo frontend uses React + Vite + MUI + ECharts, following the workbench pattern from the MIT-licensed Data Formulator project. It shows schema, distinct values, Agent intent, QuerySpec, execution metadata, result table, chart, and written insight.

Start backend API:

```bash
conda run -n medical-ai python scripts/run_demo_server.py --host 127.0.0.1 --port 8000
```

Start frontend:

```bash
cd frontend
npm install --no-audit --no-fund
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Documentation

Start every future Codex session by reading:

1. `AGENTS.md`
2. `docs/PROJECT_STATUS.md`
3. Relevant files in `docs/ROADMAP.md` and `docs/DECISIONS.md`

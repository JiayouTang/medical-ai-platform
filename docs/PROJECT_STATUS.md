# Project Status

Last updated: 2026-08-19.

## Current Phase

Phase 2 demo / early Phase 3 Agent workflow.

The current local demo is working:

```text
React/MUI/ECharts frontend
  -> demo HTTP API
  -> MedicalDataAgent
  -> DeepSeek/OpenAI-compatible LLM AgentPlan
  -> intent + tool selection + QuerySpec + ChartSpec
  -> normalization
  -> Pydantic + allowlist validation
  -> SQLAlchemy Core parameterized SQL
  -> local WSL MySQL
  -> structured JSON result
  -> DeepSeek/OpenAI-compatible LLM AgentInsight
  -> chart + table + written interpretation
```

MCP is also working through official Streamable HTTP transport:

```text
MCP Streamable HTTP client
  -> MCP server
  -> get_database_schema / get_distinct_values / query_medical_data
  -> MySQL
```

## Completed

- Created `medical-ai-platform/` as the formal project root because the parent workspace has a read-only `.git/`.
- Initialized Git in `medical-ai-platform/` on branch `main`.
- Added collaboration rules in `AGENTS.md`.
- Added project README, `.gitignore`, `.env.example`, `environment.yml`, and `pyproject.toml`.
- Created Conda environment `medical-ai` with Python 3.11.15.
- Installed project dependencies from `pyproject.toml`.
- Added required docs under `docs/`.
- Shallow-cloned reference repositories under ignored `third_party/` directories:
  - `third_party/LAMBDA` at `83cc4651c2b4e736d110af6925e1b7b8fb254cef`
  - `third_party/data-formulator` at `5477f0e236426dc8f74a498ec400414fba7fbc0f`
  - `third_party/DeepAnalyze` at `0b54741848df5c157303eb82f80a8dca1afb438f`
  - `third_party/python-sdk` at `0d92192765fa7d6a20fbfe7e62e242e44933574f`
- Added optional Docker Compose MySQL configuration under `infra/docker-compose.yml`.
- Added and verified the local WSL MySQL route.
- Created local MySQL database `medical_ai` and project user `medical_ai`.
- Stored local MySQL and DeepSeek/OpenAI-compatible credentials only in ignored `.env`.
- Implemented structured query core:
  - Pydantic `QuerySpec`
  - table and field allowlists
  - operator and aggregation allowlists
  - alias validation
  - limit enforcement
  - SQLAlchemy Core compiler
  - parameterized MySQL SQL generation
- Implemented `QueryExecutor` protocol and `MySQLExecutor`.
- Implemented official MCP SDK v2 server exposing:
  - `get_database_schema`
  - `get_distinct_values`
  - `query_medical_data`
- Verified MCP through official Streamable HTTP client on `http://127.0.0.1:3002/mcp`.
- Profiled the real SPARCS 2021 CSV in the parent workspace:
  - path: `../009 医养项目数据/Hospital_Inpatient_Discharges__SPARCS_De-Identified___2021_20231012.csv/Hospital_Inpatient_Discharges__SPARCS_De-Identified___2021_20231012.csv`
  - size: about 794 MB
  - rows: 2,101,589 including header
  - raw columns: 33
- Added streaming data cleaning helpers in `medical_ai.data.cleaning`.
- Expanded the `inpatient` schema to match the real SPARCS 2021 fields.
- Improved cleaning output with a data quality profile:
  - row count
  - null counts
  - max string lengths
  - top categorical values
  - numeric min/max values
  - invalid row sample
- Added fast MySQL load option via `LOAD DATA LOCAL INFILE`, with batch-insert fallback.
- Added common demo indexes on the `inpatient` table after loading.
- Cleaned a 1000-row real SPARCS development subset to:
  - `data/processed/inpatient_sparcs_2021_clean_1000.csv`
  - `data/processed/inpatient_sparcs_2021_clean_1000.profile.json`
- Recreated the local MySQL `inpatient` table and loaded those 1000 cleaned SPARCS rows.
- Implemented minimal OpenAI-compatible LLM client using `.env` values:
  - `LLM_BASE_URL`
  - `LLM_API_KEY`
  - `LLM_MODEL`
- Implemented `QueryPlanner` for natural-language-to-QuerySpec.
- Added LLM-output normalization for common real-model variants:
  - filter `operator` -> `op`
  - metric `function` -> `agg`
  - order `dir` -> `direction`
  - `group_by` field objects -> string fields
  - redundant metric expressions in `select`
- Added network-level retry to the minimal LLM client.
- Verified DeepSeek -> QuerySpec -> MySQL end to end on the 1000-row SPARCS subset.
- Built npm frontend demo using React + Vite + MUI + ECharts.
- Frontend follows the mature workbench direction from MIT-licensed Data Formulator: schema browser, main query/result workspace, right-side QuerySpec/execution detail panel.
- Verified frontend build and dev server.
- Added lightweight demo HTTP API in `scripts/run_demo_server.py`:
  - `GET /api/health`
  - `GET /api/schema`
  - `GET /api/distinct`
  - `POST /api/query`
  - `POST /api/ask`
- Inspected third-party workflow/agent references before the Agent enhancement:
  - `third_party/data-formulator/src/app/intentClassifier.ts`
  - `third_party/data-formulator/src/app/chartRecommendation.ts`
  - `third_party/data-formulator/src/views/workflowContext.ts`
  - `third_party/LAMBDA/backend/app/services/agent_service.py`
- Added LLM-first Agent models and orchestration:
  - `AgentIntent`
  - `ChartSpec`
  - `AgentPlan`
  - `AgentInsight`
  - `MedicalDataAgent`
- Changed `/api/ask` to return intent, tool name, tool args, analysis goal, assumptions, execution steps, QuerySpec, ChartSpec, compiled SQL, query result, and LLM-written result interpretation.
- Added a second LLM call after MySQL execution so the Agent can explain the result and chart instead of only returning a table.
- Added safe normalization for additional real LLM output variants:
  - uppercase operators, aggregations, and sort directions
  - `limit: null`
  - `count` metrics that omit `field`
- Added `scripts/demo_agent_query.py` for command-line AgentPlan -> MySQL -> AgentInsight testing.
- Enhanced the frontend demo:
  - shows Agent intent and confidence
  - shows result insight and chart-reading text
  - adds sample question chips
  - renders ECharts from backend `chart_spec`
  - supports bar, grouped bar, line, pie, number, and table fallback chart modes

## Currently Running Demo Services

- Backend demo API: `http://127.0.0.1:8000`
- Frontend Vite demo: `http://127.0.0.1:5173`

These were started by Codex in the current session. MCP Streamable HTTP is verified but not currently started in this session; restart it with the command below if needed.

## In Progress

- Full 2.1M-row SPARCS cleaning and MySQL load have not been run yet.
- Agent remains single-turn; it does not yet have a retry loop that sends validation errors back to the LLM for self-correction.
- Agent currently performs SQL-style aggregation and written interpretation only; no Python statistical analysis sandbox is implemented.
- MCP stdio transport remains unresolved in this WSL/Conda subprocess setup; Streamable HTTP is the verified MCP path.
- Frontend is a demo workbench, not a production app shell yet.

## Not Completed

- Hadoop/Spark are intentionally not configured in phase 1.
- Python code execution sandbox is intentionally not implemented.
- Full SPARCS ingestion benchmark is not recorded yet.
- Data quality rules are still basic; they do not yet enforce domain-specific validity ranges beyond parsing.
- No third-party source tree has been vendored wholesale into `src/`.

## Current Directory Structure

```text
medical-ai-platform/
  README.md
  AGENTS.md
  .gitignore
  .env.example
  .env                 # ignored local credentials
  environment.yml
  pyproject.toml
  docs/
    PROJECT_STATUS.md
    ROADMAP.md
    ARCHITECTURE.md
    ENVIRONMENT.md
    DECISIONS.md
    THIRD_PARTY.md
    DATA_CLEANING.md
  third_party/
    README.md
    LAMBDA/              # ignored reference repo
    data-formulator/     # ignored reference repo
    DeepAnalyze/         # ignored reference repo
    python-sdk/          # ignored reference repo
  data/
    raw/
      .gitkeep
    processed/
      .gitkeep
      inpatient_sparcs_2021_clean_1000.csv          # ignored generated file
      inpatient_sparcs_2021_clean_1000.profile.json # ignored generated file
    sample/
      inpatient_sample.csv
      queryspec_avg_charges_by_age.json
  src/
    medical_ai/
      config/
    data/
    db/
    query/
    mcp_server/
    agent/
      analysis_agent.py
      charting.py
      intent.py
      llm_client.py
      llm_config.py
      query_planner.py
    api/
  scripts/
    clean_sparcs_csv.py
    demo_agent_query.py
    demo_compile_query.py
    demo_llm_query.py
    demo_mcp_http_client.py
    demo_mcp_stdio_client.py
    demo_query_mysql.py
    load_sample_mysql.py
    load_sparcs_mysql.py
    run_demo_server.py
  tests/
    unit/
    integration/
  infra/
    docker-compose.yml
    mysql/
      init/
  frontend/
    README.md
    package.json
    package-lock.json
    tsconfig.json
    vite.config.ts
    index.html
    src/
      App.tsx
      api.ts
      main.tsx
      styles.css
      theme.ts
      types.ts
    node_modules/   # ignored
    dist/           # ignored
```

## Verified Commands

Data cleaning and load:

```bash
conda run -n medical-ai python scripts/clean_sparcs_csv.py --limit 1000 --output data/processed/inpatient_sparcs_2021_clean_1000.csv
conda run -n medical-ai python scripts/load_sparcs_mysql.py --csv data/processed/inpatient_sparcs_2021_clean_1000.csv --replace-table --method insert
```

Verified result:

```text
Cleaned 1000 rows into data/processed/inpatient_sparcs_2021_clean_1000.csv
Wrote profile to data/processed/inpatient_sparcs_2021_clean_1000.profile.json
Loaded 1000 cleaned SPARCS rows into inpatient in 0.73s.
inpatient row count is now 1000.
```

Tests:

```bash
conda run -n medical-ai pytest
RUN_MYSQL_TESTS=1 conda run -n medical-ai pytest tests/integration
```

Verified result:

```text
27 passed, 1 skipped
1 passed in tests/integration
```

MCP Streamable HTTP:

```bash
MCP_TRANSPORT=streamable-http MCP_PORT=3002 conda run -n medical-ai python -m medical_ai.mcp_server.server
conda run -n medical-ai python scripts/demo_mcp_http_client.py --url http://127.0.0.1:3002/mcp
```

Verified result:

```text
tools: get_database_schema, get_distinct_values, query_medical_data
AgeGroup distinct values: 0to17, 18to29, 30to49, 50to69, 70orOlder
query_medical_data returned avg_total_charges and patient_count by AgeGroup
```

LLM-to-QuerySpec:

```bash
conda run -n medical-ai python scripts/demo_llm_query.py "2021年50到69岁和70岁以上患者的平均总费用是多少，按年龄组排序" --execute
```

Verified result:

```text
50to69    avg_total_charges=73057.518979
70orOlder avg_total_charges=78913.095462
```

LLM-first Agent:

```bash
conda run -n medical-ai python scripts/demo_agent_query.py "2021年50到69岁和70岁以上患者的平均总费用是多少，按年龄组排序"
```

Verified result:

```text
intent_type=aggregate
tool_name=query_medical_data
chart_type=bar
rows:
  50to69    avg_total_charges=73057.518979
  70orOlder avg_total_charges=78913.095462
insight: 70岁以上组平均总费用更高
```

Frontend:

```bash
cd frontend
npm install --no-audit --no-fund
npm run build
npm run dev -- --host 127.0.0.1 --port 5173
```

Verified result:

```text
VITE v7.3.6 ready at http://127.0.0.1:5173/
npm run build completed successfully
```

Demo API:

```bash
conda run -n medical-ai python scripts/run_demo_server.py --host 127.0.0.1 --port 8000
```

Verified endpoints:

```text
GET  http://127.0.0.1:8000/api/health
GET  http://127.0.0.1:5173/api/health
POST http://127.0.0.1:5173/api/ask
```

`/api/health` returned:

```text
ok=true, database=medical_ai, row_count=1000, llm_configured=true
```

`POST /api/ask` through the Vite proxy was verified with:

```bash
curl -s -X POST http://127.0.0.1:5173/api/ask -H 'Content-Type: application/json' -d '{"question":"按年龄组统计2021年患者数量分布","execute":true}'
```

Verified result:

```text
intent_type=distribution
tool_name=query_medical_data
chart_type=bar
rows: 5 AgeGroup groups
insight: 30to49 group has the largest count in the current 1000-row development subset
```

## Current Environment

- WSL2 Ubuntu 24.04.3 LTS.
- Conda exists: `conda 26.1.1`.
- Conda env `medical-ai` exists at `/home/nayuta1/miniforge3/envs/medical-ai`.
- Python in `medical-ai`: `Python 3.11.15`.
- Git exists: `git version 2.43.0`.
- Node/npm exist: Node `v24.15.0`, npm `11.12.1`.
- Java exists: OpenJDK `21.0.11`.
- MySQL exists: `mysql Ver 8.0.46-0ubuntu0.24.04.3 for Linux on x86_64 ((Ubuntu))`.
- Docker is missing; not required for the current local MySQL route.
- Local MySQL database/user are configured from `.env`.
- `inpatient` currently contains 1000 cleaned SPARCS 2021 development rows.
- Frontend dependencies are installed under ignored `frontend/node_modules`.

## Credential Notes

- `.env` is ignored by Git and contains local secrets.
- `.env.example` must contain placeholders only.
- `MYSQL_PASSWORD` in `.env` is the local project database user password.
- `MYSQL_ROOT_PASSWORD` in `.env` is mainly for Docker Compose and is not used by the current apt-installed MySQL setup.
- `LLM_API_KEY` in `.env` is the local DeepSeek/OpenAI-compatible key.
- Real password or API key values must not be copied into Markdown docs or committed.

## Important Design Decisions

- Conda owns runtime; `pyproject.toml` owns Python package dependencies.
- Docker is optional. Local WSL MySQL is supported for phase-1 development.
- Phase 1 does not deploy Hadoop/Spark.
- LLMs must use structured QuerySpec, not arbitrary SQL.
- Third-party repositories live in ignored `third_party/`.
- Prefer reuse/adaptation/porting from `third_party/` before writing new modules from scratch.
- SQLAlchemy Core is used for SQL compilation/execution.
- Official MCP Python SDK v2 is used.
- SPARCS cleaning uses streaming stdlib CSV first; pandas can be added later for EDA.
- The first LLM planner uses a minimal OpenAI-compatible client before adding heavier SDKs.
- LLM JSON is normalized, then strictly validated; no free SQL is executed.
- Frontend demo uses React + Vite + MUI + ECharts after inspecting Data Formulator.
- Agent planning is LLM-first. Local code provides normalization, validation, execution, and safe chart repair, not primary intent classification.
- Result interpretation is produced by a second LLM call constrained to the returned rows, QuerySpec, chart spec, and metadata.

## Known Issues

- The parent workspace has a read-only empty `.git/` directory. The real project repository is initialized in `medical-ai-platform/`.
- Docker is not installed or not available in WSL. This does not block current development.
- MySQL `LOAD DATA LOCAL INFILE` is disabled on the server. Fast full import requires:

```bash
sudo mysql -e "SET GLOBAL local_infile = 1; SHOW GLOBAL VARIABLES LIKE 'local_infile';"
```

- `mcp.Client(mcp)` and stdio-based MCP validation hang in this environment with `mcp==2.0.0`, even for a minimal SDK example. Streamable HTTP MCP validation works and is the current verified MCP path.
- Managed sandbox blocks normal outbound socket creation and listening sockets unless commands are escalated. LLM demos and local servers require escalated execution in Codex.
- Frontend build warns that the bundle is larger than 500 kB because MUI + ECharts are included. This is acceptable for the demo and can be optimized later with code splitting.
- Full SPARCS cleaning/load is not yet benchmarked. The current verified dataset is a 1000-row development subset.
- The Agent can still fail on novel malformed LLM output because the retry/self-correction loop is not implemented yet.

## Next Steps

1. Enable MySQL `local_infile` with sudo and run full SPARCS load using `--method load-data`.
2. Add a production FastAPI backend module instead of the temporary `scripts/run_demo_server.py`.
3. Add planner retry/tool-feedback loop for invalid LLM AgentPlan or QuerySpec outputs.
4. Improve frontend interactions: chart type switching, saved example questions, execution timeline, and better error display.
5. Add data quality checks for expected domains and numeric ranges.

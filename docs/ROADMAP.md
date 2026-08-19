# Roadmap

## Phase 1 - Structured Query MVP

Goal: run a safe, testable data-query chain.

- Define `QuerySpec` JSON schema with Pydantic.
- Validate tables, fields, operators, aggregations, aliases, and limits.
- Compile safe parameterized SQL with SQLAlchemy Core.
- Execute against MySQL through a `QueryExecutor` interface.
- Expose MCP tools:
  - `get_database_schema`
  - `get_distinct_values`
  - `query_medical_data`
- Provide synthetic development data and sample queries.
- Provide scripts for cleaning and loading a SPARCS development subset.
- Keep database integration tests optional.

## Phase 1.5 - Minimal LLM Planner

- Add an OpenAI-compatible LLM client configured through `.env`.
- Convert natural-language questions to `QuerySpec`, not free-form SQL.
- Normalize common LLM JSON shape variants before strict validation.
- Keep the raw LLM response available for debugging.
- Add minimal demos that can run without a frontend.

## Phase 2 - HTTP Backend and Minimal Frontend

- Add a small HTTP API wrapping the same query service.
- Build a React + Vite + MUI + ECharts workbench demo based on Data Formulator's mature frontend direction.
- Display query result tables and simple charts.
- Add schema-aware UI controls for distinct-value inspection.
- Later decide whether to continue React/MUI or revisit Vue + ECharts.

## Phase 3 - Data Agent Workflow

- First slice completed:
  - LLM-first `AgentPlan`
  - intent and route fields
  - tool selection among schema, distinct values, and structured query
  - backend `ChartSpec`
  - execution steps
  - post-query LLM `AgentInsight`
- Add planner validation and retry loops around schema/tool feedback.
- Keep human-readable execution trace.
- Inspect DeepAnalyze and LAMBDA before implementing agent state, artifact tracking, and tool-calling workflow.

## Phase 4 - Python Analysis Sandbox

- Add controlled Python analysis for statistics, regression, correlation, clustering, anomaly detection, and complex plotting.
- Required controls before implementation:
  - sandbox isolation
  - CPU limit
  - memory limit
  - timeout
  - filesystem isolation
  - network isolation
  - package allowlist
- Never execute raw LLM output with `exec`.

## Phase 5 - Spark/Hive Scale-Out

- Preserve the executor interface:
  - `QueryExecutor`
  - `MySQLExecutor`
  - future `SparkExecutor`
  - future `HiveExecutor`
- Prefer PySpark local mode for early validation.
- Do not deploy HDFS/YARN until the MySQL MVP and product workflow are stable.

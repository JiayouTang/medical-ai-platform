# Decisions

## D001 - Python Environment Uses Conda

Date: 2026-08-18

Use Conda for Python runtime and environment management. Use `pyproject.toml` for Python package dependencies.

Rationale: the target environment is WSL with Conda already available, and reproducible runtime setup matters for human/Codex collaboration.

## D002 - Prefer MySQL Through Docker Compose

Date: 2026-08-18

Provide MySQL in `infra/docker-compose.yml` rather than installing `mysql-server` directly into WSL.

Rationale: Docker Compose is easier to reproduce and avoids mutating system packages. Current WSL environment does not have Docker, so this is configured but not verified.

Status update: superseded for the current local development machine by D009. Docker Compose remains a supported optional path, not a requirement.

## D003 - Do Not Deploy Hadoop/Spark in Phase 1

Date: 2026-08-18

Phase 1 uses MySQL plus ordinary Python. Spark/Hadoop remain future scale-out options.

Rationale: the first milestone is the correctness and safety of the query chain. If Spark validation is needed later, start with PySpark local mode before HDFS/YARN.

## D004 - Structured QuerySpec Before Free SQL

Date: 2026-08-18

The platform accepts structured `QuerySpec` JSON and compiles it to SQL. LLMs must not produce arbitrary SQL in phase 1.

Rationale: table/field/operator/aggregation allowlists and parameter binding are required for safe medical data analysis tooling.

## D005 - Third-Party Projects Stay Outside Core Source

Date: 2026-08-18

Third-party repositories, if cloned, must live under `third_party/` and be ignored by Git unless explicitly managed as submodules later.

Rationale: reference projects should not blur ownership or licensing of core platform code.

## D006 - SQLAlchemy Core for Dynamic Analysis Queries

Date: 2026-08-18

Use SQLAlchemy Core plus PyMySQL for MySQL access instead of hand-built SQL strings or full ORM CRUD.

Rationale: the main workload is dynamic filtering, grouping, aggregation, ordering, and limiting. SQLAlchemy Core provides parameter binding and composable SQL without forcing an ORM model layer.

## D007 - MCP Uses Official Python SDK v2

Date: 2026-08-18

Use the official `modelcontextprotocol/python-sdk` package line `mcp[cli]>=2,<3`.

Rationale: the current main branch README identifies v2 as the stable release line and uses `from mcp.server import MCPServer`.

## D008 - Reference-First Reuse Policy

Date: 2026-08-18

Prefer reusing, adapting, or porting mature code from `third_party/` before building new platform modules from scratch.

Rationale: the project should benefit from existing Data Agent, visualization, workflow, and code-execution projects. Reuse must still preserve clear ownership boundaries, license attribution, and dependency control.

Rules:

- Verified MIT projects can be copied or adapted when useful, with attribution.
- Projects with unverified license status can be read for architecture and UX patterns but should not have source copied.
- Direct vendoring into `src/` requires an ADR explaining source, commit, license, files reused, and why package/submodule use is not better.
- Frontend reuse is allowed. If a mature React/Next frontend is chosen over the original Vue target, document the stack change in a new ADR.

## D009 - Local MySQL Is Supported Without Docker

Date: 2026-08-18

Support local MySQL installed directly in WSL through Ubuntu packages for phase-1 development.

Rationale: Docker was unavailable in the current WSL environment and was slower for the user to operate. The project should not require Docker for the phase-1 query chain.

Rules:

- Docker Compose remains available in `infra/docker-compose.yml` for reproducible environments.
- Local MySQL credentials live in `.env`.
- Documentation must not store real passwords.
- `MYSQL_PASSWORD` is the project database user password.
- `MYSQL_ROOT_PASSWORD` is only needed for Docker Compose; local apt-installed MySQL uses `sudo mysql` administrative access.

## D010 - Stream SPARCS CSV Cleaning Before Adding Pandas

Date: 2026-08-18

Use a streaming standard-library CSV cleaner for the first SPARCS ingestion script. Pandas remains allowed for profiling, EDA, and future data quality reports.

Rationale: the real SPARCS 2021 CSV is about 794 MB with about 2.1 million lines. The first ingestion path only needs deterministic column mapping, normalization, numeric parsing, and CSV output, so a streaming script is simpler and lower memory than loading the full file into a DataFrame.

## D011 - Minimal OpenAI-Compatible LLM Client First

Date: 2026-08-18

Use a small standard-library HTTP client for the first natural-language-to-QuerySpec demo, configured by `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`.

Rationale: LAMBDA and DeepAnalyze both use OpenAI-compatible chat completion patterns, but adding the OpenAI SDK or LiteLLM is not necessary for the first demo. A later ADR can replace this client with a mature library if retries, streaming, tool calling, tracing, or multi-provider routing become important.

## D012 - Normalize LLM JSON Before Strict QuerySpec Validation

Date: 2026-08-18

The LLM planner may normalize common JSON shape variants before calling `validate_query_spec`.

Currently normalized:

- filter `operator` -> `op`
- metric `function` -> `agg`
- order `dir` -> `direction`
- `group_by` items like `{"field": "AgeGroup"}` -> `"AgeGroup"`
- redundant metric expressions in `select` for grouped aggregate queries

Rationale: real LLM calls produced these variants even with strict prompts. Normalization improves robustness while preserving the phase-1 safety boundary: only validated `QuerySpec` is compiled, and arbitrary SQL is never accepted.

## D013 - Frontend Demo Uses React + MUI + ECharts

Date: 2026-08-18

Use React + Vite + MUI + ECharts for the first visible frontend demo.

Rationale: `microsoft/data-formulator` is MIT-licensed and uses a mature React/Vite/MUI workbench architecture. Adapting that direction is lower risk and faster than forcing the original Vue target while trying to reuse a React-based mature frontend. The first demo copies the architectural pattern and visual direction, not the full Data Formulator source tree.

Status: accepted for the phase-1 demo. A later product decision can either continue on React/MUI or revisit Vue + ECharts if there is a strong reason.

## D014 - Agent Planning Is LLM-First With Safe Structured Execution

Date: 2026-08-19

Use the configured OpenAI-compatible LLM as the primary planner for user intent, tool selection, QuerySpec generation, chart recommendation, and result interpretation.

Rationale: the platform should behave like a data-analysis agent, not a keyword router. The LLM is responsible for understanding the user's analytical intent and choosing an analysis shape. Local code provides safety, normalization, deterministic execution, and fallback chart repair when the LLM references fields that are not in the query result.

Rules:

- Agent planning returns structured `AgentPlan`, not arbitrary prose.
- `AgentPlan.intent` records intent type, route, confidence, and reason.
- Query execution still requires validated `QuerySpec`; raw SQL from the LLM is not accepted.
- Result interpretation is a second LLM call based only on the executed result, QuerySpec, chart spec, and metadata.
- Local normalization may repair common JSON-shape errors such as `operator`, `function`, uppercase `ASC/DESC`, and `limit: null`.
- Local code must not replace the LLM as the primary intent recognizer.
- Frontend chart rendering follows the LLM's `chart_spec` when its referenced fields exist in the query result; otherwise backend recommends a safe chart from the validated result shape.

Third-party influence:

- Data Formulator's `intentClassifier`, `chartRecommendation`, and `workflowContext` informed the separation of intent, chart recommendation, and execution trace.
- LAMBDA's agent service informed the explicit tool/result/summary loop.
- DeepAnalyze remains a future reference for stronger multi-step data-science planning, but its model/code-execution stack is too heavy for this step.

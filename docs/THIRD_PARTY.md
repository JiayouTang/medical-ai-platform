# Third-Party Research

Research date: 2026-08-18.

The following repositories are shallow-cloned under `third_party/` for local reference and future reuse. `third_party/*` is ignored by Git except for `third_party/README.md`, so these repositories are available in the working tree but are not committed into the main project history.

```text
third_party/
  LAMBDA/
  data-formulator/
  DeepAnalyze/
  python-sdk/
```

Important: `third_party/` is not a dead archive. Future implementation work should inspect these repositories first and reuse, adapt, or port code when the license and architecture fit.

Update: the first LLM planner follows the OpenAI-compatible chat-completion configuration pattern observed in LAMBDA and DeepAnalyze, but no third-party source code was copied into `src/`. The MCP server uses the official MCP SDK as a package dependency. The frontend demo now follows Data Formulator's MIT-licensed React/Vite/MUI workbench direction and uses MUI/ECharts directly; the full Data Formulator app was not vendored because its Redux persistence, auth, connectors, editors, and visualization workflow are too broad for the phase-1 demo.

Update: the first LLM-first Agent enhancement inspected these third-party files before implementation:

- `third_party/data-formulator/src/app/intentClassifier.ts`
- `third_party/data-formulator/src/app/chartRecommendation.ts`
- `third_party/data-formulator/src/views/workflowContext.ts`
- `third_party/LAMBDA/backend/app/services/agent_service.py`

The platform adopted the architectural separation from those references: intent/tool planning, chart recommendation, execution trace, and result interpretation are separate structured objects. No third-party source code was copied into `src/` in this change.

## Summary

| Project | Best use for this platform | Phase 1 decision |
|---|---|---|
| `AMA-CMFAI/LAMBDA` | UI/workflow reference for conversational data analysis and artifact management | cloned reference; architecture/UX reuse only until license is verified |
| `microsoft/data-formulator` | Web/UI and visualization workflow reference | cloned reference; strong frontend/workflow reuse candidate |
| `ruc-datalab/DeepAnalyze` | Future Data Agent, code execution, sandbox, autonomous data science reference | cloned reference; strong future agent/sandbox reuse candidate |
| `modelcontextprotocol/python-sdk` | MCP server implementation | cloned reference and direct dependency |

## AMA-CMFAI/LAMBDA

- Repository: <https://github.com/AMA-CMFAI/LAMBDA>
- Local path: `third_party/LAMBDA`
- Inspected commit: `83cc4651c2b4e736d110af6925e1b7b8fb254cef`
- License: not verified in repository root; no license file found in shallow probe. Must verify before copying or forking code.
- README signals:
  - data analysis agent
  - React frontend
  - FastAPI backend
  - executable Python and shell tools
  - OpenAI-compatible model endpoint
  - persistent workspace and artifact tracking
- Dependency weight:
  - backend includes FastAPI, SQLAlchemy, OpenAI SDK, pandas, numpy, matplotlib, seaborn, scikit-learn, plotly, statsmodels, PDF/report tooling
  - frontend uses npm/React/TypeScript
- Fit:
  - good reference for Web/UI and analysis workflow
  - useful ideas for artifact tracking and conversation workspaces
  - not suitable as phase-1 dependency because it includes broad app/runtime behavior and code execution
- Reuse decision:
  - inspect first for conversational UI, workspace layout, artifact tracking, and OpenAI-compatible model configuration
  - do not copy source until license is verified
  - do not adopt its broad runtime/code-execution path in phase 1

## microsoft/data-formulator

- Repository: <https://github.com/microsoft/data-formulator>
- Local path: `third_party/data-formulator`
- Inspected commit: `5477f0e236426dc8f74a498ec400414fba7fbc0f`
- License: MIT
- README signals:
  - AI-powered data visualization
  - data connectors and data memory
  - data threads / branching analysis
  - database support and multiple data-source loaders
  - Flint-powered visualization
  - current README announces 0.8.0 beta 1 on 2026-08-15
- Dependency weight:
  - pandas, Flask, OpenAI, LiteLLM, DuckDB, PyArrow, database drivers, cloud SDKs, auth/session dependencies, optional Playwright and desktop packaging
- Fit:
  - strongest reference for Web/UI and visualization workflow
  - useful later for result exploration and branching conversation UX
  - too broad for phase-1 structured-query MVP
- Reuse decision:
  - primary candidate for frontend/workflow reuse
  - allowed to copy/adapt MIT-licensed components with attribution
  - phase-1 demo uses the same React/Vite/MUI direction and records that choice in D013
  - agent enhancement uses the same broad separation of intent classification, chart recommendation, and workflow trace, recorded in D014
  - do not import its broad connector/cloud dependency set into phase 1

## ruc-datalab/DeepAnalyze

- Repository: <https://github.com/ruc-datalab/DeepAnalyze>
- Local path: `third_party/DeepAnalyze`
- Inspected commit: `0b54741848df5c157303eb82f80a8dca1afb438f`
- License: MIT
- README signals:
  - autonomous data science agent
  - data preparation, analysis, modeling, visualization, report generation
  - model and training data hosted separately
  - WebUI, WebUI v2, JupyterUI, CLI
  - WebUI v2 mentions Docker-based sandbox code execution
- Dependency weight:
  - vLLM/GPU model serving path
  - torch, transformers, scientific Python stack, FastAPI, OpenAI-compatible API tooling
  - 8B model weights are not part of phase 1
- Fit:
  - best reference for Data Agent, code execution, and data-analysis workflow
  - useful for future sandbox design and autonomous analysis patterns
  - too heavy for phase 1 and should not be downloaded with model weights now
- Reuse decision:
  - primary candidate for future Data Agent, sandbox, and code-execution workflow reuse
  - allowed to copy/adapt MIT-licensed code with attribution when phase 2/3 reaches that scope
  - no model weights, vLLM setup, or GPU dependency in phase 1

## Current Agent Reuse Notes

- Data Formulator is still the best frontend/workflow reference. Its intent classifier uses an LLM routing call rather than English-only keyword matching; our `MedicalDataAgent` follows the same LLM-first principle.
- Data Formulator's chart recommendation layer maps model chart intent to concrete UI chart types; our backend now returns a small `ChartSpec`, and the frontend resolves it into ECharts options.
- Data Formulator's workflow context records user messages, tool calls, created tables, and created charts; our `AgentPlan.execution_steps`, compiled SQL metadata, result, and `AgentInsight` are the smaller phase-1 version of that trace.
- LAMBDA's `AgentService` shows an explicit tool registry and result-summary loop. Our phase-1 agent has fixed safe tools only: schema, distinct values, and structured medical data query. We are not adopting its Python/shell execution tools yet.

## modelcontextprotocol/python-sdk

- Repository: <https://github.com/modelcontextprotocol/python-sdk>
- Local path: `third_party/python-sdk`
- Inspected commit: `0d92192765fa7d6a20fbfe7e62e242e44933574f`
- License: MIT
- README signals:
  - official Python implementation of MCP
  - v2 is the current stable release line
  - supports stdio, Streamable HTTP, and SSE
  - server API uses `from mcp.server import MCPServer`
  - Python 3.10+
- Dependency weight:
  - acceptable for phase 1
  - `mcp[cli]` adds CLI tooling for local dev
- Fit:
  - required dependency for MCP server
- Reuse decision:
  - direct dependency in `pyproject.toml` as `mcp[cli]>=2,<3`
  - local clone is for API inspection and examples, not vendoring the protocol implementation

## Direct Answers

- Suitable Web/UI reference: `microsoft/data-formulator`, then `AMA-CMFAI/LAMBDA`.
- Suitable Data Agent reference: `ruc-datalab/DeepAnalyze`, then `AMA-CMFAI/LAMBDA`.
- Suitable Code Execution reference: `ruc-datalab/DeepAnalyze` for sandbox direction; `AMA-CMFAI/LAMBDA` for workspace/artifact behavior. Neither should be copied into phase 1.
- Suitable data-analysis workflow reference: all three; `data-formulator` is strongest for visualization workflow, `DeepAnalyze` for autonomous analysis workflow.
- Heavy dependencies: `DeepAnalyze` is heaviest due to model/vLLM/GPU; `data-formulator` is broad due to data loaders/cloud/browser/desktop; `LAMBDA` is full-stack with reporting and code execution.
- Suitable for phase 1: `modelcontextprotocol/python-sdk` as a direct dependency; Data Formulator/LAMBDA/DeepAnalyze as local reference repos.
- Fork or reference: keep local shallow clones under `third_party/`; copy/adapt MIT code only with attribution and ADR.

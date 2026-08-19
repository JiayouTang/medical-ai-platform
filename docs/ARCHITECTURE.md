# Architecture

## Final Direction

```text
Natural language question
  -> LLM / Data Agent
  -> analysis plan
  -> data analysis tools
  -> SQL / Spark execution
  -> structured data
  -> optional Python secondary analysis
  -> charts + tables + written insights
```

## Phase 1 Runtime

```text
QuerySpec JSON
  -> Pydantic model
  -> QueryValidator
  -> QueryCompiler
  -> ExecutableQuery
  -> QueryExecutor
  -> MySQLExecutor
  -> QueryResult JSON
```

Current natural-language path:

```text
User question
  -> MedicalDataAgent
  -> OpenAI-compatible LLM planning call
  -> AgentPlan
       - intent
       - tool_name
       - QuerySpec
       - ChartSpec
       - execution_steps
  -> AgentPlan normalization
  -> QuerySpec validation
  -> QueryCompiler
  -> MySQLExecutor
  -> structured QueryResult
  -> OpenAI-compatible LLM result-interpretation call
  -> AgentInsight
       - summary
       - chart_reading
       - observations
       - limitations
       - follow_up_questions
```

Current frontend demo path:

```text
React/Vite/MUI workbench
  -> Vite proxy /api
  -> scripts/run_demo_server.py
  -> MedicalDataAgent or query_medical_data
  -> MySQLExecutor
  -> ECharts rendering from Agent chart_spec
```

## Boundaries

- `medical_ai.data` owns raw-to-canonical data cleaning helpers for development datasets.
- `medical_ai.query` owns structured query models, validation, and SQL compilation.
- `medical_ai.db` owns schema allowlists and execution.
- `medical_ai.mcp_server` owns MCP tool registration and thin tool wrappers.
- `medical_ai.agent` owns provider-neutral LLM configuration, LLM-first planning, chart recommendation, and result interpretation.
- `medical_ai.api` is reserved for a future production HTTP backend.
- `scripts/run_demo_server.py` is the current lightweight demo HTTP API.
- `frontend/` owns the React + Vite + MUI + ECharts demo workbench.
- `third_party/` is for reference repositories only, not core source.

## Security Model for Phase 1

- No arbitrary SQL input.
- LLM output is normalized only into structured `AgentPlan` and `QuerySpec`; it is never executed as SQL.
- No write operation tools.
- Static table allowlist.
- Static field allowlist.
- Operator allowlist.
- Aggregation allowlist.
- Alias pattern allowlist.
- Parameter binding through SQLAlchemy Core.
- Maximum result limit.
- Distinct-value limit.
- MySQL query timeout setting where supported by the server.

## Data Model Scope

The `inpatient` table is aligned with NY SPARCS 2021 de-identified hospital inpatient discharge fields:

- `HospitalServiceArea`
- `HospitalCounty`
- `OperatingCertificateNumber`
- `PermanentFacilityId`
- `FacilityName`
- `AgeGroup`
- `ZipCode3Digits`
- `Gender`
- `Race`
- `Ethnicity`
- `RaceEthnicity`
- `LengthOfStay`
- `AdmissionType`
- `PatientDisposition`
- `DischargeYear`
- `CCSRDiagnosisCode`
- `CCSRDiagnosisDescription`
- `CCSRProcedureCode`
- `CCSRProcedureDescription`
- `APRDRGCode`
- `APRDRGDescription`
- `APRMDCCode`
- `APRMDCDescription`
- `APRSeverityOfIllnessCode`
- `APRSeverityOfIllnessDescription`
- `APRRiskOfMortality`
- `APRMedicalSurgicalDescription`
- `PaymentTypology1`
- `PaymentTypology2`
- `PaymentTypology3`
- `BirthWeight`
- `EmergencyDepartmentIndicator`
- `TotalCharges`
- `TotalCosts`

`data/sample/inpatient_sample.csv` is synthetic development data only. Cleaned SPARCS development files under `data/processed/` are generated locally and ignored by Git.

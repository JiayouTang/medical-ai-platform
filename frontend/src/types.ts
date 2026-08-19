export interface HealthPayload {
  ok: boolean;
  database: string;
  row_count: number;
  llm_configured: boolean;
  elapsed_ms: number;
}

export interface SchemaColumn {
  name: string;
  type: string;
  description: string;
  allowed_operations: string[];
  numeric: boolean;
}

export interface SchemaPayload {
  tables: Array<{
    name: string;
    description: string;
    columns: SchemaColumn[];
  }>;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, string | number | boolean | null>[];
  row_count: number;
  query_time_ms: number;
  truncated: boolean;
  metadata: Record<string, unknown>;
}

export interface AgentIntent {
  intent_type: string;
  route: string;
  confidence: number;
  reason: string;
}

export interface ChartSpec {
  chart_type: 'table' | 'bar' | 'grouped_bar' | 'line' | 'pie' | 'number';
  x_field?: string | null;
  y_field?: string | null;
  series_field?: string | null;
  title: string;
  reason: string;
}

export interface AgentInsight {
  summary: string;
  chart_reading: string;
  observations: string[];
  limitations: string[];
  follow_up_questions: string[];
}

export interface AskPayload {
  question: string;
  intent?: AgentIntent;
  tool_name?: string;
  tool_args?: Record<string, unknown>;
  analysis_goal?: string;
  assumptions?: string[];
  execution_steps?: string[];
  query_spec: Record<string, unknown> | null;
  chart_spec?: ChartSpec | null;
  compiled_sql: string | null;
  compiled_params: Record<string, unknown>;
  result?: QueryResult;
  tool_result?: Record<string, unknown>;
  insight?: AgentInsight | null;
}

export interface DistinctPayload {
  table: string;
  field: string;
  values: Array<string | number | null>;
  row_count: number;
  truncated: boolean;
  query_time_ms: number;
}

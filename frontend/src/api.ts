import type { AskPayload, DistinctPayload, HealthPayload, QueryResult, SchemaPayload } from './types';

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed with ${response.status}`);
  }
  return payload as T;
}

export function getHealth(): Promise<HealthPayload> {
  return requestJson<HealthPayload>('/api/health');
}

export function getSchema(): Promise<SchemaPayload> {
  return requestJson<SchemaPayload>('/api/schema');
}

export function getDistinct(field: string): Promise<DistinctPayload> {
  return requestJson<DistinctPayload>(`/api/distinct?table=inpatient&field=${encodeURIComponent(field)}&limit=30`);
}

export function ask(question: string): Promise<AskPayload> {
  return requestJson<AskPayload>('/api/ask', {
    method: 'POST',
    body: JSON.stringify({ question, execute: true }),
  });
}

export async function runQuerySpec(querySpec: Record<string, unknown>): Promise<QueryResult> {
  const payload = await requestJson<{ result: QueryResult }>('/api/query', {
    method: 'POST',
    body: JSON.stringify({ query_spec: querySpec }),
  });
  return payload.result;
}

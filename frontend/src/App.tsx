import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactElement, ReactNode } from 'react';
import * as echarts from 'echarts';
import {
  Alert,
  AppBar,
  Box,
  Button,
  Chip,
  CircularProgress,
  CssBaseline,
  Divider,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  ThemeProvider,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import StorageIcon from '@mui/icons-material/Storage';
import SchemaIcon from '@mui/icons-material/Schema';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import TableRowsIcon from '@mui/icons-material/TableRows';
import { ask, getDistinct, getHealth, getSchema, runQuerySpec } from './api';
import { theme } from './theme';
import type {
  AgentInsight,
  AgentIntent,
  AskPayload,
  ChartSpec,
  DistinctPayload,
  HealthPayload,
  QueryResult,
  SchemaColumn,
  SchemaPayload,
} from './types';

const defaultQuestion = '2021年50到69岁和70岁以上患者的平均总费用是多少，按年龄组排序';
const sampleSpec = {
  table: 'inpatient',
  filters: [
    { field: 'DischargeYear', op: '=', value: 2021 },
    { field: 'AgeGroup', op: 'in', value: ['50to69', '70orOlder'] },
  ],
  group_by: ['AgeGroup'],
  metrics: [
    { field: 'TotalCharges', agg: 'avg', alias: 'avg_total_charges' },
    { field: '*', agg: 'count', alias: 'patient_count' },
  ],
  order_by: [{ field: 'avg_total_charges', direction: 'desc' }],
  limit: 100,
};

const sampleQuestions = [
  '按年龄组统计2021年患者数量分布',
  '2021年不同入院类型的平均住院天数排名前10',
  '比较不同支付方式的平均总费用',
  '2021年急诊和非急诊患者的平均总费用有什么差异',
];

export function App() {
  const [health, setHealth] = useState<HealthPayload | null>(null);
  const [schema, setSchema] = useState<SchemaPayload | null>(null);
  const [distinct, setDistinct] = useState<DistinctPayload | null>(null);
  const [question, setQuestion] = useState(defaultQuestion);
  const [querySpecText, setQuerySpecText] = useState(JSON.stringify(sampleSpec, null, 2));
  const [askResult, setAskResult] = useState<AskPayload | null>(null);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadBasics = useCallback(async () => {
    setError(null);
    try {
      const [nextHealth, nextSchema] = await Promise.all([getHealth(), getSchema()]);
      setHealth(nextHealth);
      setSchema(nextSchema);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  useEffect(() => {
    void loadBasics();
  }, [loadBasics]);

  const handleAsk = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = await ask(question);
      setAskResult(payload);
      if (payload.query_spec) {
        setQuerySpecText(JSON.stringify(payload.query_spec, null, 2));
      }
      setQueryResult(payload.result ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleRunSpec = async () => {
    setLoading(true);
    setError(null);
    try {
      const parsed = JSON.parse(querySpecText) as Record<string, unknown>;
      const payload = await runQuerySpec(parsed);
      setAskResult(null);
      setQueryResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDistinct = async (field: string) => {
    setError(null);
    try {
      setDistinct(await getDistinct(field));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const columns = schema?.tables[0]?.columns ?? [];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static" color="inherit" elevation={0} sx={{ border: 0, borderBottom: '1px solid rgba(16,24,40,0.12)' }}>
          <Toolbar sx={{ minHeight: 68, gap: 2, justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="h1">Medical AI Workbench</Typography>
              <Typography variant="body2" color="text.secondary">
                SPARCS inpatient discharge analysis demo
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" justifyContent="flex-end">
              <StatusChip icon={<StorageIcon />} label={health ? `MySQL ${health.database}` : 'MySQL'} ok={Boolean(health?.ok)} />
              <Chip size="small" label={health ? `${health.row_count.toLocaleString()} rows` : 'Rows --'} />
              <StatusChip icon={<SmartToyIcon />} label={health?.llm_configured ? 'LLM configured' : 'LLM missing'} ok={Boolean(health?.llm_configured)} />
              <Tooltip title="Refresh">
                <IconButton size="small" onClick={() => void loadBasics()}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
          </Toolbar>
        </AppBar>

        <Box
          component="main"
          sx={{
            flex: 1,
            minHeight: 0,
            p: 1.5,
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', lg: '310px minmax(480px, 1fr) 430px' },
            gap: 1.5,
          }}
        >
          <SchemaPanel columns={columns} distinct={distinct} onDistinct={handleDistinct} />

          <Stack spacing={1.5} minWidth={0} minHeight={0}>
            <Paper sx={{ p: 1.5 }}>
              <SectionTitle icon={<SmartToyIcon />} title="Ask" secondary="Natural language -> QuerySpec -> MySQL" />
              <TextField
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                multiline
                minRows={4}
                fullWidth
                sx={{ mt: 1.5 }}
              />
              <Stack direction="row" flexWrap="wrap" gap={0.75} sx={{ mt: 1.25 }}>
                {sampleQuestions.map((sample) => (
                  <Chip key={sample} size="small" label={sample} onClick={() => setQuestion(sample)} />
                ))}
              </Stack>
              <Stack direction="row" spacing={1} sx={{ mt: 1.5 }}>
                <Button startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <PlayArrowIcon />} variant="contained" onClick={handleAsk} disabled={loading}>
                  Run Agent
                </Button>
                <Button variant="outlined" onClick={() => setQuerySpecText(JSON.stringify(sampleSpec, null, 2))}>
                  Load Sample QuerySpec
                </Button>
              </Stack>
            </Paper>

            {error ? <Alert severity="error">{error}</Alert> : null}

            <Paper sx={{ minHeight: 0, display: 'grid', gridTemplateRows: 'auto auto 280px minmax(240px, 1fr)' }}>
              <Box sx={{ p: 1.5, pb: 0 }}>
                <SectionTitle
                  icon={<QueryStatsIcon />}
                  title="Result"
                  secondary={
                    askResult?.intent
                      ? `${askResult.intent.intent_type} · ${(askResult.intent.confidence * 100).toFixed(0)}%`
                      : queryResult
                        ? `${queryResult.row_count} rows in ${queryResult.query_time_ms} ms`
                        : 'Waiting for query'
                  }
                />
              </Box>
              <InsightPanel insight={askResult?.insight ?? null} intent={askResult?.intent ?? null} />
              <ResultChart result={queryResult} chartSpec={askResult?.chart_spec ?? null} />
              <ResultTable result={queryResult} />
            </Paper>
          </Stack>

          <Paper sx={{ minWidth: 0, minHeight: { xs: 520, lg: 0 }, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 1.5, pb: 0 }}>
              <SectionTitle
                icon={<SchemaIcon />}
                title="QuerySpec"
                secondary="Strict JSON, not SQL"
                action={
                  <Tooltip title="Run QuerySpec">
                    <IconButton size="small" onClick={handleRunSpec} disabled={loading}>
                      <PlayArrowIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                }
              />
            </Box>
            <TextField
              value={querySpecText}
              onChange={(event) => setQuerySpecText(event.target.value)}
              multiline
              spellCheck={false}
              sx={{
                flex: '1 1 48%',
                m: 1.5,
                '& textarea': {
                  fontFamily: '"Roboto Mono", Consolas, monospace',
                  fontSize: 12,
                  lineHeight: 1.5,
                },
              }}
              minRows={12}
            />
            <Divider />
            <Box sx={{ p: 1.5 }}>
              <SectionTitle icon={<TableRowsIcon />} title="Execution" secondary="Compiled SQL and params" />
              <Box
                component="pre"
                sx={{
                  mt: 1,
                  mb: 0,
                  maxHeight: 260,
                  overflow: 'auto',
                  p: 1.25,
                  borderRadius: 1,
                  bgcolor: '#101828',
                  color: '#f8fafc',
                  fontSize: 12,
                  lineHeight: 1.45,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {executionText(askResult, queryResult)}
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

function StatusChip({ icon, label, ok }: { icon: ReactElement; label: string; ok: boolean }) {
  return <Chip size="small" icon={icon} label={label} color={ok ? 'success' : 'default'} variant={ok ? 'filled' : 'outlined'} />;
}

function SectionTitle({ icon, title, secondary, action }: { icon: ReactNode; title: string; secondary?: string; action?: ReactNode }) {
  return (
    <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
      <Stack direction="row" alignItems="center" spacing={1} minWidth={0}>
        <Box sx={{ color: 'primary.main', display: 'flex' }}>{icon}</Box>
        <Box minWidth={0}>
          <Typography variant="h2">{title}</Typography>
          {secondary ? (
            <Typography variant="caption" color="text.secondary" noWrap>
              {secondary}
            </Typography>
          ) : null}
        </Box>
      </Stack>
      {action}
    </Stack>
  );
}

function SchemaPanel({ columns, distinct, onDistinct }: { columns: SchemaColumn[]; distinct: DistinctPayload | null; onDistinct: (field: string) => void }) {
  return (
    <Paper sx={{ minHeight: { xs: 360, lg: 0 }, display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1.5 }}>
        <SectionTitle icon={<SchemaIcon />} title="Schema" secondary={`${columns.length} allowlisted fields`} />
        <Stack direction="row" flexWrap="wrap" gap={0.75} sx={{ mt: 1.5 }}>
          {['AgeGroup', 'Gender', 'AdmissionType', 'PaymentTypology1', 'CCSRDiagnosisDescription'].map((field) => (
            <Chip key={field} size="small" label={field} onClick={() => onDistinct(field)} />
          ))}
        </Stack>
        <Box sx={{ mt: 1.5, p: 1, minHeight: 66, maxHeight: 120, overflow: 'auto', border: '1px solid rgba(16,24,40,0.12)', borderRadius: 1, bgcolor: '#fcfcfd' }}>
          <Typography variant="caption" color="text.secondary">
            {distinct ? `${distinct.field}: ${distinct.values.join(', ')}${distinct.truncated ? ' ...' : ''}` : 'Click a chip to inspect distinct values.'}
          </Typography>
        </Box>
      </Box>
      <Divider />
      <List dense sx={{ overflow: 'auto', flex: 1, py: 0 }}>
        {columns.map((column) => (
          <ListItemButton key={column.name} onClick={() => onDistinct(column.name)} sx={{ alignItems: 'flex-start', borderBottom: '1px solid rgba(16,24,40,0.08)' }}>
            <ListItemText
              primary={
                <Stack direction="row" justifyContent="space-between" spacing={1}>
                  <Typography variant="body2" fontWeight={700}>
                    {column.name}
                  </Typography>
                  <Typography variant="caption" color={column.numeric ? 'secondary.main' : 'primary.main'}>
                    {column.type}
                  </Typography>
                </Stack>
              }
              secondary={column.description}
              secondaryTypographyProps={{ fontSize: 11, lineHeight: 1.35 }}
            />
          </ListItemButton>
        ))}
      </List>
    </Paper>
  );
}

function InsightPanel({ insight, intent }: { insight: AgentInsight | null; intent: AgentIntent | null }) {
  if (!insight && !intent) {
    return <Box sx={{ px: 1.5, py: 1 }} />;
  }
  return (
    <Box sx={{ px: 1.5, py: 1 }}>
      {insight ? (
        <Stack spacing={0.75}>
          <Typography variant="body2" fontWeight={700}>
            {insight.summary}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {insight.chart_reading}
          </Typography>
          {insight.observations.length ? (
            <Stack direction="row" flexWrap="wrap" gap={0.75}>
              {insight.observations.slice(0, 3).map((item) => (
                <Chip key={item} size="small" label={item} />
              ))}
            </Stack>
          ) : null}
        </Stack>
      ) : intent ? (
        <Typography variant="caption" color="text.secondary">
          {intent.reason}
        </Typography>
      ) : null}
    </Box>
  );
}

function ResultChart({ result, chartSpec }: { result: QueryResult | null; chartSpec: ChartSpec | null }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const chartColumns = result?.columns ?? [];
  const rows = useMemo(() => result?.rows ?? [], [result]);

  useEffect(() => {
    if (!ref.current) return;
    const instance = echarts.init(ref.current);
    const fields = resolveChartFields(result, chartSpec);
    if (!result || !fields.xField || !fields.yField || rows.length === 0 || fields.chartType === 'table') {
      instance.setOption({
        title: { text: 'No chartable result yet', left: 'center', top: 'middle', textStyle: { color: '#667085', fontSize: 13, fontWeight: 400 } },
      });
    } else {
      instance.setOption(buildChartOption(rows, fields, chartSpec), true);
    }
    const resize = () => instance.resize();
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
      instance.dispose();
    };
  }, [chartColumns, chartSpec, result, rows]);

  return <Box ref={ref} sx={{ minHeight: 0, borderBottom: '1px solid rgba(16,24,40,0.12)' }} />;
}

function resolveChartFields(result: QueryResult | null, chartSpec: ChartSpec | null) {
  const rows = result?.rows ?? [];
  const columns = result?.columns ?? [];
  const firstRow = rows[0] ?? {};
  const numericColumns = columns.filter((column) => typeof firstRow[column] === 'number');
  const labelColumns = columns.filter((column) => typeof firstRow[column] !== 'number');
  const xField = pickExisting(columns, chartSpec?.x_field) ?? labelColumns[0] ?? columns[0];
  const yField = pickExisting(columns, chartSpec?.y_field) ?? numericColumns.find((column) => column !== xField);
  const seriesField = pickExisting(columns, chartSpec?.series_field);
  const chartType = chartSpec?.chart_type ?? (seriesField ? 'grouped_bar' : 'bar');
  return { chartType, xField, yField, seriesField };
}

function pickExisting(columns: string[], field?: string | null) {
  return field && columns.includes(field) ? field : undefined;
}

function buildChartOption(
  rows: QueryResult['rows'],
  fields: { chartType: string; xField: string; yField: string; seriesField?: string },
  chartSpec: ChartSpec | null,
): echarts.EChartsOption {
  const { chartType, xField, yField, seriesField } = fields;
  const title = chartSpec?.title ?? yField;

  if (chartType === 'number') {
    return {
      title: { text: title, left: 'center', top: 20, textStyle: { color: '#344054', fontSize: 14 } },
      graphic: {
        type: 'text',
        left: 'center',
        top: 'middle',
        style: { text: formatCell(rows[0]?.[yField]), fill: '#101828', fontSize: 34, fontWeight: 700 },
      },
    };
  }

  if (chartType === 'pie') {
    return {
      title: { text: title, left: 16, top: 8, textStyle: { color: '#344054', fontSize: 13 } },
      tooltip: { trigger: 'item' },
      legend: { type: 'scroll', bottom: 0, textStyle: { color: '#667085' } },
      series: [
        {
          type: 'pie',
          radius: ['38%', '68%'],
          center: ['50%', '48%'],
          data: rows.map((row) => ({ name: String(row[xField]), value: Number(row[yField] ?? 0) })),
        },
      ],
    };
  }

  if (seriesField || chartType === 'grouped_bar') {
    const xValues = uniqueValues(rows.map((row) => String(row[xField])));
    const seriesValues = uniqueValues(rows.map((row) => String(row[seriesField ?? xField])));
    return {
      title: { text: title, left: 16, top: 8, textStyle: { color: '#344054', fontSize: 13 } },
      grid: { left: 64, right: 24, top: 56, bottom: 42 },
      tooltip: { trigger: 'axis' },
      legend: { top: 28, textStyle: { color: '#667085' } },
      xAxis: { type: 'category', data: xValues, axisLabel: { color: '#344054' } },
      yAxis: { type: 'value', axisLabel: { color: '#667085' } },
      series: seriesValues.map((value) => ({
        name: value,
        type: chartType === 'line' ? 'line' : 'bar',
        smooth: chartType === 'line',
        data: xValues.map((xValue) => {
          const row = rows.find((candidate) => String(candidate[xField]) === xValue && String(candidate[seriesField ?? xField]) === value);
          return Number(row?.[yField] ?? 0);
        }),
      })),
    };
  }

  return {
    title: { text: title, left: 16, top: 8, textStyle: { color: '#344054', fontSize: 13 } },
    grid: { left: 68, right: 24, top: 52, bottom: 42 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: rows.map((row) => String(row[xField])), axisLabel: { color: '#344054' } },
    yAxis: { type: 'value', axisLabel: { color: '#667085' } },
    series: [
      {
        type: chartType === 'line' ? 'line' : 'bar',
        smooth: chartType === 'line',
        data: rows.map((row) => Number(row[yField] ?? 0)),
        itemStyle: { color: '#0f6cbd', borderRadius: chartType === 'bar' ? [4, 4, 0, 0] : 0 },
      },
    ],
  };
}

function uniqueValues(values: string[]) {
  return Array.from(new Set(values));
}

function ResultTable({ result }: { result: QueryResult | null }) {
  if (!result) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography color="text.secondary">Run a question or QuerySpec to see table results.</Typography>
      </Box>
    );
  }
  return (
    <TableContainer sx={{ minHeight: 0 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            {result.columns.map((column) => (
              <TableCell key={column}>{column}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {result.rows.map((row, index) => (
            <TableRow key={index}>
              {result.columns.map((column) => (
                <TableCell key={column} align={typeof row[column] === 'number' ? 'right' : 'left'}>
                  {formatCell(row[column])}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function formatCell(value: unknown) {
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 3 });
  }
  if (value === null || value === undefined || value === '') {
    return '--';
  }
  return String(value);
}

function executionText(askResult: AskPayload | null, queryResult: QueryResult | null) {
  if (askResult) {
    return JSON.stringify(
      {
        intent: askResult.intent,
        tool_name: askResult.tool_name,
        analysis_goal: askResult.analysis_goal,
        execution_steps: askResult.execution_steps,
        chart_spec: askResult.chart_spec,
        compiled_sql: askResult.compiled_sql,
        compiled_params: askResult.compiled_params,
        metadata: askResult.result?.metadata,
      },
      null,
      2,
    );
  }
  if (queryResult) {
    return JSON.stringify({ metadata: queryResult.metadata }, null, 2);
  }
  return 'Ready.';
}

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from medical_ai.agent.intent import AgentIntent, IntentType
from medical_ai.query.models import Aggregation, QuerySpec


class ChartType(str, Enum):
    TABLE = "table"
    BAR = "bar"
    GROUPED_BAR = "grouped_bar"
    LINE = "line"
    PIE = "pie"
    NUMBER = "number"


class ChartSpec(BaseModel):
    chart_type: ChartType
    x_field: str | None = None
    y_field: str | None = None
    series_field: str | None = None
    title: str
    reason: str

    model_config = ConfigDict(extra="forbid")


def recommend_chart(
    query_spec: QuerySpec | None,
    result: dict[str, Any] | None,
    intent: AgentIntent | IntentType | str | None = None,
) -> ChartSpec:
    if query_spec is None:
        return ChartSpec(
            chart_type=ChartType.TABLE,
            title="Result",
            reason="no QuerySpec is available",
        )

    group_fields = list(query_spec.group_by or query_spec.select)
    metric_aliases = [metric.alias for metric in query_spec.metrics]
    first_metric = metric_aliases[0] if metric_aliases else None
    row_count = int((result or {}).get("row_count") or 0)

    if not query_spec.metrics:
        return ChartSpec(
            chart_type=ChartType.TABLE,
            title="Detail rows",
            reason="query returns raw detail rows rather than aggregate measures",
        )

    if not group_fields:
        return ChartSpec(
            chart_type=ChartType.NUMBER,
            y_field=first_metric,
            title=_title_for_metric(first_metric),
            reason="single aggregate without grouping",
        )

    if row_count == 0:
        return ChartSpec(
            chart_type=ChartType.TABLE,
            x_field=group_fields[0],
            y_field=first_metric,
            title="No chartable rows",
            reason="the query returned no rows",
        )

    intent_type = _intent_type(intent)

    if intent_type is IntentType.TREND or "DischargeYear" in group_fields:
        return ChartSpec(
            chart_type=ChartType.LINE,
            x_field="DischargeYear" if "DischargeYear" in group_fields else group_fields[0],
            y_field=first_metric,
            series_field=_series_field(group_fields, preferred_x="DischargeYear"),
            title=_title_for_metric(first_metric),
            reason="trend questions or year-grouped results are best read as a line chart",
        )

    if intent_type is IntentType.DISTRIBUTION and len(group_fields) == 1 and _is_count_query(query_spec):
        return ChartSpec(
            chart_type=ChartType.PIE,
            x_field=group_fields[0],
            y_field=first_metric,
            title=_title_for_metric(first_metric),
            reason="single-dimension count distributions can be shown as a pie chart",
        )

    if len(group_fields) >= 2:
        return ChartSpec(
            chart_type=ChartType.GROUPED_BAR,
            x_field=group_fields[0],
            y_field=first_metric,
            series_field=group_fields[1],
            title=_title_for_metric(first_metric),
            reason="two grouped dimensions are displayed as a grouped bar chart",
        )

    return ChartSpec(
        chart_type=ChartType.BAR,
        x_field=group_fields[0],
        y_field=first_metric,
        title=_title_for_metric(first_metric),
        reason="one grouped dimension and one aggregate measure are displayed as a bar chart",
    )


def _is_count_query(query_spec: QuerySpec) -> bool:
    return bool(query_spec.metrics) and query_spec.metrics[0].agg is Aggregation.COUNT


def _intent_type(intent: AgentIntent | IntentType | str | None) -> IntentType | None:
    if intent is None:
        return None
    if isinstance(intent, AgentIntent):
        return intent.intent_type
    if isinstance(intent, IntentType):
        return intent
    try:
        return IntentType(intent)
    except ValueError:
        return None


def _series_field(group_fields: list[str], preferred_x: str) -> str | None:
    for field in group_fields:
        if field != preferred_x:
            return field
    return None


def _title_for_metric(metric_alias: str | None) -> str:
    if not metric_alias:
        return "Query result"
    return metric_alias.replace("_", " ").title()

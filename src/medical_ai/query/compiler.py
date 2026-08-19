from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.dialects import mysql

from medical_ai.db.schema import build_sqlalchemy_table, column_names
from medical_ai.query.models import Aggregation, FilterOperator, QuerySpec, SortDirection
from medical_ai.query.validator import validate_query_spec


@dataclass(frozen=True)
class ExecutableQuery:
    statement: Select[Any]
    sql: str
    params: dict[str, Any]
    table: str
    limit: int


class QueryCompiler:
    def compile(self, spec: QuerySpec) -> ExecutableQuery:
        spec = validate_query_spec(spec)
        table = build_sqlalchemy_table(spec.table)
        columns = table.c

        metric_expressions: dict[str, Any] = {}

        if spec.metrics:
            dimension_fields = spec.group_by or spec.select
            select_expressions = [columns[field] for field in dimension_fields]

            for metric in spec.metrics:
                expression = self._metric_expression(metric.agg, metric.field, columns).label(metric.alias)
                metric_expressions[metric.alias] = expression
                select_expressions.append(expression)

            statement = select(*select_expressions).select_from(table)
            if dimension_fields:
                statement = statement.group_by(*(columns[field] for field in dimension_fields))
        else:
            selected_fields = spec.select or spec.group_by or column_names(spec.table)
            statement = select(*(columns[field] for field in selected_fields)).select_from(table)
            if spec.group_by:
                statement = statement.group_by(*(columns[field] for field in spec.group_by))

        for filter_spec in spec.filters:
            statement = statement.where(self._filter_expression(filter_spec.op, columns[filter_spec.field], filter_spec.value))

        for order_spec in spec.order_by:
            expression = metric_expressions.get(order_spec.field, columns.get(order_spec.field))
            if expression is None:
                raise ValueError(f"Cannot order by unknown expression {order_spec.field!r}")
            statement = statement.order_by(desc(expression) if order_spec.direction is SortDirection.DESC else asc(expression))

        statement = statement.limit(spec.limit)
        sql, params = compile_statement(statement)
        return ExecutableQuery(statement=statement, sql=sql, params=params, table=spec.table, limit=spec.limit)

    def _metric_expression(self, agg: Aggregation, field: str, columns: Any) -> Any:
        if agg is Aggregation.COUNT and field == "*":
            return func.count()

        column = columns[field]
        if agg is Aggregation.COUNT:
            return func.count(column)
        if agg is Aggregation.SUM:
            return func.sum(column)
        if agg is Aggregation.AVG:
            return func.avg(column)
        if agg is Aggregation.MIN:
            return func.min(column)
        if agg is Aggregation.MAX:
            return func.max(column)
        raise ValueError(f"Unsupported aggregation {agg!r}")

    def _filter_expression(self, op: FilterOperator, column: Any, value: Any) -> Any:
        if op is FilterOperator.EQ:
            return column == value
        if op is FilterOperator.NE:
            return column != value
        if op is FilterOperator.GT:
            return column > value
        if op is FilterOperator.GTE:
            return column >= value
        if op is FilterOperator.LT:
            return column < value
        if op is FilterOperator.LTE:
            return column <= value
        if op is FilterOperator.IN:
            return column.in_(list(value))
        if op is FilterOperator.NOT_IN:
            return column.not_in(list(value))
        if op is FilterOperator.BETWEEN:
            low, high = value
            return column.between(low, high)
        if op is FilterOperator.LIKE:
            return column.like(value)
        if op is FilterOperator.IS_NULL:
            return column.is_(None)
        if op is FilterOperator.IS_NOT_NULL:
            return column.is_not(None)
        raise ValueError(f"Unsupported operator {op!r}")


def compile_statement(statement: Select[Any]) -> tuple[str, dict[str, Any]]:
    compiled = statement.compile(
        dialect=mysql.dialect(paramstyle="pyformat"),
        compile_kwargs={"render_postcompile": True},
    )
    return str(compiled), dict(compiled.params)


def compile_query(data: QuerySpec | dict[str, Any]) -> ExecutableQuery:
    spec = validate_query_spec(data)
    return QueryCompiler().compile(spec)

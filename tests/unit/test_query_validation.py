import pytest

from medical_ai.query import QueryValidationError, validate_query_spec


def base_query() -> dict:
    return {
        "table": "inpatient",
        "filters": [{"field": "DischargeYear", "op": "=", "value": 2021}],
        "group_by": ["AgeGroup"],
        "metrics": [
            {"field": "TotalCharges", "agg": "avg", "alias": "avg_total_charges"},
            {"field": "*", "agg": "count", "alias": "patient_count"},
        ],
        "order_by": [{"field": "avg_total_charges", "direction": "desc"}],
        "limit": 100,
    }


def test_valid_query_spec_passes() -> None:
    spec = validate_query_spec(base_query())
    assert spec.table == "inpatient"
    assert spec.metrics[0].alias == "avg_total_charges"


def test_invalid_table_rejected() -> None:
    query = base_query()
    query["table"] = "inpatient; DROP TABLE inpatient"

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_invalid_field_rejected() -> None:
    query = base_query()
    query["filters"][0]["field"] = "NotAField"

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_invalid_operator_rejected() -> None:
    query = base_query()
    query["filters"][0]["op"] = "contains"

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_limit_enforced() -> None:
    query = base_query()
    query["limit"] = 1001

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_raw_sql_extra_field_rejected() -> None:
    query = base_query()
    query["sql"] = "DROP TABLE inpatient"

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_only_count_can_use_star_metric() -> None:
    query = base_query()
    query["metrics"] = [{"field": "*", "agg": "avg", "alias": "bad_avg"}]

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_avg_requires_numeric_field() -> None:
    query = base_query()
    query["metrics"] = [{"field": "AgeGroup", "agg": "avg", "alias": "bad_avg"}]

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)


def test_in_filter_requires_non_empty_list() -> None:
    query = base_query()
    query["filters"] = [{"field": "AgeGroup", "op": "in", "value": []}]

    with pytest.raises(QueryValidationError):
        validate_query_spec(query)

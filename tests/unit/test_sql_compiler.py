from medical_ai.query import compile_query


def test_compile_aggregate_query_to_parameterized_mysql_sql() -> None:
    query = compile_query(
        {
            "table": "inpatient",
            "filters": [
                {"field": "DischargeYear", "op": "=", "value": 2021},
                {"field": "AgeGroup", "op": "in", "value": ["50to69", "70orOlder"]},
            ],
            "group_by": ["AgeGroup"],
            "metrics": [
                {"field": "TotalCharges", "agg": "avg", "alias": "avg_total_charges"},
                {"field": "*", "agg": "count", "alias": "patient_count"},
            ],
            "order_by": [{"field": "avg_total_charges", "direction": "desc"}],
            "limit": 100,
        }
    )

    assert "SELECT" in query.sql
    assert "FROM inpatient" in query.sql
    assert "WHERE" in query.sql
    assert "GROUP BY" in query.sql
    assert "ORDER BY" in query.sql
    assert "LIMIT" in query.sql
    assert 2021 in query.params.values()
    assert "50to69" in query.params.values()
    assert "70orOlder" in query.params.values()


def test_compile_does_not_inline_filter_values() -> None:
    dangerous = "x'; DROP TABLE inpatient; --"
    query = compile_query(
        {
            "table": "inpatient",
            "select": ["FacilityName"],
            "filters": [{"field": "FacilityName", "op": "=", "value": dangerous}],
            "limit": 5,
        }
    )

    assert "DROP TABLE" not in query.sql
    assert dangerous in query.params.values()


def test_compile_between_and_null_filters() -> None:
    query = compile_query(
        {
            "table": "inpatient",
            "select": ["FacilityName", "TotalCharges"],
            "filters": [
                {"field": "TotalCharges", "op": "between", "value": [10000, 50000]},
                {"field": "PaymentTypology1", "op": "is_not_null"},
            ],
            "order_by": [{"field": "TotalCharges", "direction": "asc"}],
            "limit": 10,
        }
    )

    assert "BETWEEN" in query.sql
    assert "IS NOT NULL" in query.sql
    assert 10000 in query.params.values()
    assert 50000 in query.params.values()

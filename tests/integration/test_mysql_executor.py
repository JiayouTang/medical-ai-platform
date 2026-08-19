import os

import pytest

from medical_ai.db import MySQLExecutor
from medical_ai.query import compile_query

pytestmark = pytest.mark.integration


@pytest.mark.skipif(os.getenv("RUN_MYSQL_TESTS") != "1", reason="Set RUN_MYSQL_TESTS=1 and configure MySQL to run.")
def test_mysql_executor_count_query() -> None:
    query = compile_query(
        {
            "table": "inpatient",
            "metrics": [{"field": "*", "agg": "count", "alias": "patient_count"}],
            "limit": 1,
        }
    )

    result = MySQLExecutor().execute(query)

    assert result.columns == ["patient_count"]
    assert result.row_count == 1

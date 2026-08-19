import json

from medical_ai.agent.analysis_agent import MedicalDataAgent, normalize_agent_plan
from medical_ai.agent.intent import IntentType
from medical_ai.db.executor import QueryResult


class FakeAgentClient:
    def __init__(self, plan_payload: dict | None = None) -> None:
        self.calls = 0
        self.plan_payload = plan_payload or _valid_plan_payload()

    def chat_json(self, messages, max_tokens=1200):
        self.calls += 1
        if self.calls == 1:
            return json.dumps(self.plan_payload)
        return json.dumps(
            {
                "summary": "70岁以上组的平均总费用更高。",
                "chart_reading": "柱状图按年龄组展示平均总费用，柱越高表示平均收费越高。",
                "observations": ["70orOlder 高于 50to69", "结果包含 2 个年龄组"],
                "limitations": ["这是开发样例数据，不能代表完整医疗结论"],
                "follow_up_questions": ["是否按入院类型进一步拆分？"],
            },
            ensure_ascii=False,
        )


class FakeExecutor:
    def execute(self, query):
        return QueryResult(
            columns=["AgeGroup", "avg_total_charges", "patient_count"],
            rows=[
                {"AgeGroup": "70orOlder", "avg_total_charges": 78913.1, "patient_count": 202},
                {"AgeGroup": "50to69", "avg_total_charges": 73057.5, "patient_count": 284},
            ],
            row_count=2,
            query_time_ms=7.5,
            metadata={"table": "inpatient", "limit": 100},
        )


def test_medical_data_agent_runs_llm_plan_execute_and_interpret() -> None:
    client = FakeAgentClient()
    run = MedicalDataAgent(client=client, executor=FakeExecutor()).run(
        "比较2021年50到69岁和70岁以上患者的平均总费用",
        execute=True,
        interpret=True,
    )

    assert client.calls == 2
    assert run.plan.intent.intent_type is IntentType.COMPARISON
    assert run.plan.query_spec is not None
    assert run.compiled_query is not None
    assert run.result is not None
    assert run.insight is not None
    assert run.plan.chart_spec is not None
    assert run.plan.chart_spec.chart_type.value == "bar"
    assert "70岁以上" in run.insight.summary


def test_normalize_agent_plan_accepts_common_llm_aliases() -> None:
    normalized = normalize_agent_plan(
        {
            "intent": "ranking",
            "intent_confidence": 0.82,
            "tool": "query_medical_data",
            "querySpec": {
                "table": "inpatient",
                "filters": [{"field": "DischargeYear", "operator": "=", "value": 2021}],
                "group_by": [{"field": "AdmissionType"}],
                "metrics": [{"field": "*", "function": "count", "alias": "patient_count"}],
                "order_by": [{"field": "patient_count", "dir": "desc"}],
                "limit": 10,
            },
            "chart": {"type": "bar", "x": "AdmissionType", "y": "patient_count"},
        }
    )

    assert normalized["intent"]["intent_type"] == "ranking"
    assert normalized["intent"]["route"] == "query"
    assert normalized["tool_name"] == "query_medical_data"
    assert normalized["query_spec"]["filters"][0]["op"] == "="
    assert normalized["query_spec"]["group_by"] == ["AdmissionType"]
    assert normalized["query_spec"]["metrics"][0]["agg"] == "count"
    assert normalized["chart_spec"]["chart_type"] == "bar"


def test_agent_recommends_chart_when_llm_chart_references_missing_field() -> None:
    payload = _valid_plan_payload()
    payload["chart_spec"] = {
        "chart_type": "bar",
        "x_field": "AgeGroup",
        "y_field": "not_in_result",
        "title": "Bad chart",
        "reason": "bad field",
    }
    run = MedicalDataAgent(client=FakeAgentClient(payload), executor=FakeExecutor()).run(
        "比较2021年不同年龄组的平均总费用",
        execute=True,
        interpret=False,
    )

    assert run.plan.chart_spec is not None
    assert run.plan.chart_spec.y_field == "avg_total_charges"


def _valid_plan_payload() -> dict:
    return {
        "intent": {
            "intent_type": "comparison",
            "route": "query",
            "confidence": 0.91,
            "reason": "The user asks to compare average charges across age groups.",
        },
        "tool_name": "query_medical_data",
        "tool_args": {},
        "analysis_goal": "Compare average total charges by age group for 2021.",
        "query_spec": {
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
        },
        "chart_spec": {
            "chart_type": "bar",
            "x_field": "AgeGroup",
            "y_field": "avg_total_charges",
            "title": "Average Total Charges by Age Group",
            "reason": "A bar chart compares average charges across age groups.",
        },
        "assumptions": ["Use TotalCharges for 总费用."],
        "execution_steps": ["Classify intent", "Create QuerySpec", "Execute query", "Interpret result"],
    }

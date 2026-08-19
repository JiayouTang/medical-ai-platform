from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IntentType(str, Enum):
    SCHEMA_LOOKUP = "schema_lookup"
    DISTINCT_VALUES = "distinct_values"
    AGGREGATE = "aggregate"
    COMPARISON = "comparison"
    TREND = "trend"
    DISTRIBUTION = "distribution"
    RANKING = "ranking"
    DETAIL_LOOKUP = "detail_lookup"
    UNSUPPORTED = "unsupported"


class AgentRoute(str, Enum):
    SCHEMA = "schema"
    DISTINCT = "distinct"
    QUERY = "query"
    UNSUPPORTED = "unsupported"


class AgentIntent(BaseModel):
    intent_type: IntentType
    route: AgentRoute
    confidence: float = Field(ge=0, le=1)
    reason: str

    model_config = ConfigDict(extra="forbid")

from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class ModelParametersSearchCost:
    cpt_low: float
    cpt_medium: float
    cpt_high: float


@dataclass
class ModelParameters:
    model_identifier: str
    model_provider: str
    context_window_size: int
    cpm_non_cached_input_tokens_dollars: float
    cpm_cached_input_tokens_dollars: float
    cpm_completion_tokens_dollars: float
    search_cost: Optional[ModelParametersSearchCost] = None


@dataclass
class TokenUsage:
    input_tokens: int
    cached_input_tokens: int
    completion_tokens: int


@dataclass
class TokenUsageCost:
    non_cached_input_tokens_cost: float
    cached_input_tokens_cost: float
    completion_tokens_cost: float
    search_cost: float
    total_cost: float


class UsageDescription(Enum):
    SEARCH = "search"
    STRUCTURED_COMPLETION = "structured_completion"
    COMPLETION = "completion"


class ModelProvider(Enum):
    OPENAI = "OpenAI"
    GOOGLE = "Google"

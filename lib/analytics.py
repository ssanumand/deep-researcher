from abc import ABC, abstractmethod
from typing import Literal, Optional

from google.genai.types import GenerateContentResponseUsageMetadata
from openai.types import CompletionUsage

from lib.constants import LLMIdentifier
from lib.log import logger
from lib.types import UsageDescription


# XXX: Only for LLM-based Crawlers
class Analytics(ABC):
    def __init__(self):
        self.total_calls: int = 0
        self.search_calls: int = 0

        self.total_input_tokens: int = 0
        self.total_cached_input_tokens: int = 0
        self.total_completion_tokens: int = 0

    @abstractmethod
    def update_stats(
        self,
        usage_stats: CompletionUsage,
        usage_description: UsageDescription,
    ) -> None: ...

    @abstractmethod
    def total_cost(
        self,
        llm_model: LLMIdentifier,
        search_context_size: Optional[Literal["low", "medium", "high"]] = None,
    ) -> float: ...


class LLMAnalytics(Analytics):
    def update_stats(
        self,
        usage_stats: CompletionUsage | GenerateContentResponseUsageMetadata,
        usage_description: UsageDescription,
    ) -> None:
        logger.debug("Analytics: Usage Stats: %s", usage_description.value)

        if isinstance(usage_stats, CompletionUsage):
            logger.debug(
                "Analytics: Prompt Tokens: %d\nCached Tokens: %d\nCompletion "
                "Tokens: %d",
                usage_stats.prompt_tokens,
                usage_stats.prompt_tokens_details.cached_tokens,
                usage_stats.completion_tokens,
            )

            self.total_input_tokens += usage_stats.prompt_tokens
            self.total_cached_input_tokens += (
                usage_stats.prompt_tokens_details.cached_tokens
            )
            self.total_completion_tokens += usage_stats.completion_tokens
        elif isinstance(usage_stats, GenerateContentResponseUsageMetadata):
            cached_content_token_count = (
                usage_stats.cached_content_token_count
                if usage_stats.cached_content_token_count
                else 0
            )

            logger.debug(
                "Analytics: Prompt Token Count: %d\nCached Content Token "
                "Count: %d\nCandidates Token Count: %d",
                usage_stats.prompt_token_count,
                cached_content_token_count,
                usage_stats.candidates_token_count,
            )

            self.total_input_tokens += usage_stats.prompt_token_count
            self.total_cached_input_tokens += cached_content_token_count
            self.total_completion_tokens += usage_stats.candidates_token_count

        self.search_calls += usage_description == UsageDescription.SEARCH
        self.total_calls += 1

    def total_cost(
        self,
        llm_model: LLMIdentifier,
        search_context_size: Optional[Literal["low", "medium", "high"]] = None,
    ) -> float:
        logger.debug(
            "Analytics: Total Calls: %d\nSearch Calls: %d",
            self.total_calls,
            self.search_calls,
        )

        non_cached_input_tokens_cost = (
            (self.total_input_tokens - self.total_cached_input_tokens) / 10_00_000
        ) * llm_model.value.cpm_non_cached_input_tokens_dollars
        cached_input_tokens_cost = (
            self.total_cached_input_tokens
            / 10_00_000
            * llm_model.value.cpm_cached_input_tokens_dollars
        )
        completion_tokens_cost = (
            self.total_completion_tokens
            / 10_00_000
            * llm_model.value.cpm_completion_tokens_dollars
        )

        search_cost = 0
        if search_context_size:
            search_cost = getattr(
                llm_model.value.search_cost,
                f"cpt_{search_context_size}",
            )
            search_cost = self.search_calls / 1_000 * search_cost

        logger.debug(
            "Analytics: Non-Cached Input Tokens Cost: $%f\nCached Input "
            "Tokens Cost: $%f\nCompletion Tokens Cost: $%f\nSearch Cost: "
            "$%f",
            non_cached_input_tokens_cost,
            cached_input_tokens_cost,
            completion_tokens_cost,
            search_cost,
        )

        return (
            non_cached_input_tokens_cost
            + cached_input_tokens_cost
            + completion_tokens_cost
            + search_cost
        )

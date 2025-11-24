from enum import Enum

from lib.types import ModelParameters, ModelParametersSearchCost, ModelProvider


class LLMIdentifier(Enum):
    O3_MINI = ModelParameters(
        model_identifier="o3-mini",
        model_provider=ModelProvider.OPENAI,
        context_window_size=200_000,
        cpm_non_cached_input_tokens_dollars=1.10,
        cpm_cached_input_tokens_dollars=0.55,
        cpm_completion_tokens_dollars=4.40,
    )
    O1 = ModelParameters(
        model_identifier="o1",
        model_provider=ModelProvider.OPENAI,
        context_window_size=200_000,
        cpm_non_cached_input_tokens_dollars=15.00,
        cpm_cached_input_tokens_dollars=7.50,
        cpm_completion_tokens_dollars=60.00,
    )
    O1_MINI = ModelParameters(
        model_identifier="o1-mini",
        model_provider=ModelProvider.OPENAI,
        context_window_size=128_000,
        cpm_non_cached_input_tokens_dollars=1.10,
        cpm_cached_input_tokens_dollars=0.55,
        cpm_completion_tokens_dollars=4.40,
    )
    GPT_4O = ModelParameters(
        model_identifier="gpt-4o",
        model_provider=ModelProvider.OPENAI,
        context_window_size=128_000,
        cpm_non_cached_input_tokens_dollars=2.50,
        cpm_cached_input_tokens_dollars=1.25,
        cpm_completion_tokens_dollars=10.00,
        search_cost=ModelParametersSearchCost(
            cpt_low=30.00, cpt_medium=35.00, cpt_high=50.00
        ),
    )
    GPT_4O_MINI = ModelParameters(
        model_identifier="gpt-4o-mini",
        model_provider=ModelProvider.OPENAI,
        context_window_size=128_000,
        cpm_non_cached_input_tokens_dollars=0.15,
        cpm_cached_input_tokens_dollars=0.075,
        cpm_completion_tokens_dollars=0.60,
        search_cost=ModelParametersSearchCost(
            cpt_low=25.00, cpt_medium=27.50, cpt_high=30.00
        ),
    )
    GEMINI_2_0_FLASH = ModelParameters(
        model_identifier="gemini-2.0-flash",
        model_provider=ModelProvider.GOOGLE,
        context_window_size=1_000_000,
        cpm_non_cached_input_tokens_dollars=0.10,
        cpm_cached_input_tokens_dollars=0.025,
        cpm_completion_tokens_dollars=0.40,
    )
    GEMINI_2_0_FLASH_LITE = ModelParameters(
        model_identifier="gemini-2.0-flash-lite",
        model_provider=ModelProvider.GOOGLE,
        context_window_size=1_000_000,
        cpm_non_cached_input_tokens_dollars=0.075,
        cpm_cached_input_tokens_dollars=0.30,
        cpm_completion_tokens_dollars=0.40,
    )

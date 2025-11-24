from enum import Enum
from os import path

from lib.log import logger


class PromptTemplates(Enum):
    SYSTEM_PROMPT = "system_prompt"
    USER_PROMPT__SERP_QUERY_GENERATION = "up_serp_query_generation"
    USER_PROMPT__QUERY_REFINEMENT = "up_query_refinement"
    USER_PROMPT__QUERY_GENERATION_ADDON__AUTO_REFINEMENT_QUERY = (
        "up_serp_addon_query_auto_refinement"
    )
    USER_PROMPT__QUERY_GENERATION_ADDON__PREVIOUS_RESEARCH_DETAILS = (
        "up_serp_addon_previous_research_details"
    )
    USER_PROMPT__LEARNING_GENERATION = "up_learning_generation"
    USER_PROMPT__REPORT_GENERATION = "up_report_generation"


# Singleton Factory
class PromptFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance

        logger.debug("Creating: PromptFactory")
        cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._prompts = {
            PromptTemplates.SYSTEM_PROMPT: "",
            PromptTemplates.USER_PROMPT__SERP_QUERY_GENERATION: "",
            PromptTemplates.USER_PROMPT__QUERY_GENERATION_ADDON__AUTO_REFINEMENT_QUERY: "",
            PromptTemplates.USER_PROMPT__QUERY_GENERATION_ADDON__PREVIOUS_RESEARCH_DETAILS: "",
            PromptTemplates.USER_PROMPT__QUERY_REFINEMENT: "",
            PromptTemplates.USER_PROMPT__LEARNING_GENERATION: "",
            PromptTemplates.USER_PROMPT__REPORT_GENERATION: "",
        }

        self._load_prompts()

    def _load_prompts(self):
        logger.debug("Loading Prompts")
        base_path = path.dirname(path.abspath(__file__))

        for prompt in self._prompts:
            with open(
                path.join(base_path, "prompts", f"{prompt.value}.md"),
                "r",
                encoding="utf-8",
            ) as f:
                self._prompts[prompt] = f.read()

    def get_prompt(self, prompt_template: PromptTemplates, **kwargs):
        logger.debug("Fetched Prompt: %s", prompt_template.name)
        return self._prompts[prompt_template].format(**kwargs)

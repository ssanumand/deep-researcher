from os import getenv

from dotenv import load_dotenv
from google.genai import Client
from openai import OpenAI

from lib.analytics import LLMAnalytics
from lib.constants import LLMIdentifier
from lib.crawlers import GeminiSearchCrawler, OpenAISearchCrawler
from lib.llm import OpenAICompatibleLLMModel
from lib.models.llm import DeepResearchHyperParameters
from lib.researcher import DeepResearcher


def main():
    load_dotenv(".env.local")

    openai_client = OpenAI()
    researcher = DeepResearcher(
        crawler=GeminiSearchCrawler(
            llm_identifier=LLMIdentifier.GEMINI_2_0_FLASH,
            llm_instance=Client(api_key=getenv("GEMINI_API_KEY")),
        ),
        llm_model=OpenAICompatibleLLMModel(
            llm_identifier=LLMIdentifier.GPT_4O, llm_instance=openai_client
        ),
        analytics_instance=LLMAnalytics(),
        research_parameters=DeepResearchHyperParameters(
            num_learnings=5,
            num_refinement_questions=3,
            learning_depth=5,
            learning_width=3,
        ),
    )

    with open("./assets/query.md", "r", encoding="utf-8") as file_handle:
        user_query = file_handle.read().strip()

    learnings, report = researcher(
        user_query=user_query,
        auto_query_refinement=True,
    )

    with open("./assets/learnings.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(learnings))

    with open("./assets/report.md", "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()

from time import perf_counter
from typing import Optional

from openai.types import CompletionUsage
from pydantic import BaseModel

from lib.analytics import Analytics
from lib.config import DeepResearchHyperParameters
from lib.crawlers import Crawler, LLMCrawler
from lib.llm import LLMModel
from lib.log import logger
from lib.models.crawler import SERPQuerySearchResults
from lib.models.llm import (
    Learning,
    SERPQueries,
    UserQueryRefinementQuestions,
)
from lib.types import UsageDescription


class DeepResearcher:
    def __init__(
        self,
        crawler: Crawler | LLMCrawler,
        llm_model: LLMModel,
        research_parameters: Optional[DeepResearchHyperParameters] = None,
        analytics_instance: Optional[Analytics] = None,
    ):
        self.crawler = crawler
        self.llm_model = llm_model
        self.research_parameters = research_parameters or DeepResearchHyperParameters(
            num_refinement_questions=3,
            num_learnings=3,
            learning_width=3,
            learning_depth=2,
        )
        self.analytics_instance = analytics_instance

        self.final_learnings = []

    def __call__(self, user_query: str, auto_query_refinement: bool = False):
        start_time_s = perf_counter()

        logger.info("Starting Deep Researcher")
        logger.debug("User Query: %s", user_query)
        logger.debug("LLM: %s", self.llm_model)
        logger.debug("Crawler: %s", self.crawler)
        logger.debug("Research Parameters: %s", self.research_parameters)
        logger.debug(
            "Analytics: %s",
            "Enabled" if self.analytics_instance else "Disabled",
        )

        if auto_query_refinement:
            logger.info("Query Refinement: Auto")
            user_query = (
                USER_PROMPT__QUERY_GENERATION_ADDON__AUTO_REFINEMENT_QUERY.format(
                    user_query=user_query
                )
            )
        else:
            logger.info("Query Refinement: Manual")
            new_questions = self._refine_user_query(user_query=user_query)
            answers = self._prompt_user_for_answers(questions=new_questions)

            logger.info("Generated: %d Follow-up Questions", len(new_questions))
            user_query += "\n\nFollow-up Questions and Answers:\n" + "\n\n".join([
                f"Question: {question}\nAnswer: {answer}"
                for question, answer in zip(new_questions, answers, strict=False)
            ])
        self.run(
            width=self.research_parameters.learning_width,
            depth=0,
            user_query=user_query,
            learnings=[],
        )

        report = self._generate_report(user_query=user_query)
        logger.debug("Generated: %d Learnings", len(self.final_learnings))
        logger.info("Deep Researcher Completed")

        if self.analytics_instance:
            cost = self.analytics_instance.total_cost(
                llm_model=self.llm_model.llm_identifier,
                search_context_size=self.crawler.search_context_size,  # None | "low" | "medium" | "high"
            )
            logger.info("Total Cost: $%f", cost)

        end_time_s = perf_counter() - start_time_s
        logger.info("Execution Time: %.2f seconds", end_time_s)
        return self.final_learnings, report

    def _prompt_user_for_answers(self, questions: list[str]) -> list[str]:
        return [input(f"{question}: ") for question in questions]

    def run(
        self,
        width: int,
        depth: int,
        user_query: str,
        learnings: list[str],
    ) -> None:
        logger.info("Running Deep Researcher")
        logger.debug(
            "Width: %d | Depth: %d",
            width,
            depth,
        )
        logger.debug("User Query: %s", user_query)

        serp_queries = self._generate_serp_queries(
            user_query=user_query, width=width
        ).queries

        logger.info("Generated: %d SERP Queries", len(serp_queries))
        logger.debug(
            "SERP Queries:\n%s",
            serp_queries,
        )

        for serp_query in serp_queries:
            if depth == 0:
                learnings.clear()

            if isinstance(self.crawler, LLMCrawler):
                logger.info("Crawler: LLM-based")
                serp_data = self._search_query(
                    query=f"Query: {serp_query.query}\nResearch Goal: {serp_query.research_goal}"
                )
            else:
                logger.info("Crawler: Non-LLM-based")
                serp_data = self._search_query(query=serp_query.query)

            learnings_followup_questions_serp_query = (
                f"SERP Query: {serp_query.query}\n"
                f"Research Goal: {serp_query.research_goal}"
            )
            learning, follow_up_queries = (
                self._generate_learnings_and_follow_up_questions(
                    serp_query=learnings_followup_questions_serp_query,
                    serp_data=serp_data,
                )
            )

            learnings.append(learning)
            self.final_learnings.append(
                learnings_followup_questions_serp_query + "\nLearnings: " + learning
            )
            new_user_query = (
                USER_PROMPT__QUERY_GENERATION_ADDON__PREVIOUS_RESEARCH_DETAILS.format(
                    previous_research_goal=serp_query.research_goal,
                    learnings=learnings,
                    follow_up_questions=follow_up_queries,
                )
            )

            new_depth = depth + 1
            if new_depth < self.research_parameters.learning_depth:
                self.run(
                    width=self.research_parameters.calculate_width_for_depth(
                        depth=new_depth
                    ),
                    depth=new_depth,
                    user_query=new_user_query,
                    learnings=learnings,
                )
            else:
                logger.debug("Max Depth Reached")

    def _refine_user_query(self, user_query) -> list[str]:
        logger.info("Refining User Query")
        return self._generate_llm_response(
            user_prompt=USER_PROMPT__QUERY_REFINEMENT.format(
                num_questions=self.research_parameters.num_refinement_questions,
                query=user_query,
            ),
            response_format=UserQueryRefinementQuestions,
        ).questions

    def _generate_serp_queries(self, user_query: str, width: int) -> SERPQueries:
        logger.info("Generating SERP Queries")

        return self._generate_llm_response(
            user_prompt=USER_PROMPT__SERP_QUERY_GENERATION.format(
                num_queries=width, query_addon=user_query
            ),
            response_format=SERPQueries,
        )

    def _generate_learnings_and_follow_up_questions(
        self, serp_query: str, serp_data: SERPQuerySearchResults | str
    ) -> list[str]:
        logger.info("Generating Learnings and Follow-up Questions")

        if isinstance(serp_data, SERPQuerySearchResults):
            serp_data = "\n\n".join([
                (
                    f"Title: {result.title}\nDescription: "
                    f"{result.description}\nContent: {result.content}"
                    f"\nURL: {result.url}"
                )
                for result in serp_data.search_results
            ])

        response = self._generate_llm_response(
            user_prompt=USER_PROMPT__LEARNING_GENERATION.format(
                num_learnings=self.research_parameters.num_learnings,
                serp_query=serp_query,
                serp_data=serp_data,
            ),
            response_format=Learning,
        )

        return response.learning, response.follow_up_queries

    def _generate_report(self, user_query: str) -> str:
        logger.info("Generating Report")
        return self._generate_llm_response(
            user_prompt=USER_PROMPT__REPORT_GENERATION.format(
                user_query=user_query, learnings=self.final_learnings
            ),
        )

    def _search_query(self, query: str) -> SERPQuerySearchResults:
        response, usage = self.crawler.search(query)

        if self.analytics_instance:
            self.analytics_instance.update_stats(
                usage_stats=usage,
                usage_description=UsageDescription.SEARCH,
            )

            return response

    def _generate_llm_response(
        self, user_prompt: str, response_format: Optional[BaseModel] = None
    ) -> tuple[BaseModel | str, CompletionUsage]:
        response, usage = self.llm_model.generate_llm_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_format=response_format,
        )

        if self.analytics_instance:
            self.analytics_instance.update_stats(
                usage_stats=usage,
                usage_description=(
                    UsageDescription.STRUCTURED_COMPLETION
                    if response_format
                    else UsageDescription.COMPLETION
                ),
            )

        return response

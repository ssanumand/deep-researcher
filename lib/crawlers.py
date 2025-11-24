from abc import ABC, abstractmethod
from os import getenv
from re import sub as re_sub
from typing import Literal, Optional

from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    GenerateContentResponseUsageMetadata,
    GoogleSearch,
    Tool,
)
from openai import OpenAI
from openai.types import CompletionUsage
from requests import post as rpost

from lib.constants import LLMIdentifier
from lib.log import logger
from lib.models.crawler import SERPQuerySearchResult, SERPQuerySearchResults
from lib.types import ModelProvider


class Crawler(ABC):
    @abstractmethod
    def search(self, query: str) -> SERPQuerySearchResults: ...

    @abstractmethod
    def crawl(self, link: str) -> str:
        raise NotImplementedError("Unsupported Operation")


class LLMCrawler(ABC):
    def __init__(
        self,
        llm_identifier: LLMIdentifier,
        llm_instance: OpenAI | Client,
        search_context_size: Optional[Literal["low", "medium", "high"]] = None,
    ):
        if isinstance(llm_instance, OpenAI) and not search_context_size:
            raise ValueError(
                "Required: search_context_size (OpenAI-based web search)"
            )

        if (
            isinstance(llm_instance, OpenAI)
            and llm_identifier.value.model_provider != ModelProvider.OPENAI
        ) or (
            isinstance(llm_instance, Client)
            and llm_identifier.value.model_provider != ModelProvider.GOOGLE
        ):
            raise ValueError("Mismatch: LLM Model Provider and LLM Instance")

        self.llm_identifier = llm_identifier
        self.llm_instance = llm_instance
        self.search_context_size = search_context_size

    @abstractmethod
    def search(self, query: str) -> tuple[
        SERPQuerySearchResults | str,
        CompletionUsage | GenerateContentResponseUsageMetadata,
    ]: ...


class FirecrawlCrawler(Crawler):
    def __init__(self, crawl_limit: int = 3):
        self.crawl_limit = crawl_limit

        self.SEARCH_URL = "https://api.firecrawl.dev/v1/search"
        self._APIK_KEY = getenv("FIRECRAWL_API_KEY")

    def search(self, query: str) -> SERPQuerySearchResults:
        logger.info("Searching Query: %s", query)

        headers = {
            "Authorization": f"Bearer {self._APIK_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "query": query,
            "limit": self.crawl_limit,
            "timeout": 60000,
            "scrapeOptions": {"formats": ["markdown"]},
        }

        response = rpost(
            self.SEARCH_URL, headers=headers, json=data, timeout=60000
        )

        logger.info("Response Code: %d", response.status_code)

        if response.status_code == 200:
            return SERPQuerySearchResults(
                search_results=[
                    SERPQuerySearchResult(
                        title=result["title"],
                        description=result["description"],
                        content=self._clean_text(result["markdown"]),
                        url=result["url"],
                    )
                    for result in response.json()["data"]
                ]
            )

        if response.status_code == 408:
            logger.error("Firecrawl: Request Timeout")
            raise RuntimeError("Rate Limit Exceeded")

        if response.status_code == 500:
            logger.error("Firecrawl: Internal Server Error")
            raise RuntimeError("Internal Server Error")

    def _clean_text(self, text: str) -> str:
        # Non-ASCII
        text = re_sub(r"[^\x00-\x7F]+", "", text)
        # Continuous Newlines OR Continuous Whitespaces -> Single Whitespace
        text = re_sub(r"\n+|\s+", " ", text)
        # Remove Markdown Links
        text = re_sub(r"\[.*?\]\(.*?\)", "", text)
        return text


class OpenAISearchCrawler(LLMCrawler):
    def __init__(
        self,
        llm_identifier: LLMIdentifier,
        llm_instance: OpenAI,
        search_context_size: Literal["low", "medium", "high"],
    ):
        super().__init__(llm_identifier, llm_instance, search_context_size)

    def search(
        self, query: str
    ) -> tuple[SERPQuerySearchResults | str, CompletionUsage]:
        logger.info("Searching Query: %s", query)

        try:
            response = self.llm_instance.responses.create(
                model=self.llm_identifier.value.model_identifier,
                tools=[
                    {
                        "type": "web_search_preview",
                        "search_context_size": self.search_context_size,
                    }
                ],
                input=query,
                timeout=120000,
            )
        except TimeoutError:
            logger.error("OpenAI: Request Timeout for Query: %s", query)
            logger.warning("Returning Empty Response")
            return "", CompletionUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            )

        return response.output_text, response.usage


class GeminiSearchCrawler(LLMCrawler):
    def __init__(
        self,
        llm_identifier: LLMIdentifier,
        llm_instance: Client,
        search_context_size: Optional[Literal["low", "medium", "high"]] = None,
    ):
        super().__init__(llm_identifier, llm_instance, search_context_size)

    def search(
        self, query: str
    ) -> tuple[
        SERPQuerySearchResults | str, GenerateContentResponseUsageMetadata
    ]:
        logger.info("Searching Query: %s", query)

        response = self.llm_instance.models.generate_content(
            model=self.llm_identifier.value.model_identifier,
            contents=query,
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
                response_modalities=["TEXT"],
            ),
        )

        return response.text, response.usage_metadata

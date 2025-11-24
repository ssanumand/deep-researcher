from dataclasses import dataclass


@dataclass
class SERPQuerySearchResult:
    title: str
    description: str
    content: str
    url: str

    def __repr__(self):
        return (
            f"SERPQuerySearchResult("
            f"title={self.title}, "
            f"description={self.description}, "
            f"content={self.content}, "
            f"url={self.url})"
        )


@dataclass
class SERPQuerySearchResults:
    search_results: list[SERPQuerySearchResult]

    def __repr__(self):
        return (
            f"SERPQuerySearchResults(search_results={self.search_results})"
        )

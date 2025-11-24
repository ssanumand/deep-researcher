from pydantic import BaseModel, Field


class SERPQuery(BaseModel):
    query: str = Field(..., title="SERP Query")
    research_goal: str = Field(
        ...,
        title="Research Goal",
        description=(
            "First, talk about the goal of the research that this query is "
            "meant to accomplish. Then, go deeper into how to advance the "
            "research once the results are found, mentioning additional "
            "research directions. Be as specific as possible, especially for "
            "additional research directions."
        ),
    )


class SERPQueries(BaseModel):
    queries: list[SERPQuery] = Field(..., title="List of SERP Queries")


class UserQueryRefinementQuestions(BaseModel):
    questions: list[str] = Field(
        ...,
        title="List of User Query Refinement Questions",
        description=("Follow up questions to clarify the research direction."),
    )


class Learning(BaseModel):
    learning: str = Field(
        ...,
        title="Learnings from Data",
        description=(
            "Generate a concise, data-driven insight from SERP "
            "analysis. Provide actionable, specific information highlighting "
            "key patterns or trends. Ensure insights are evidence-based with "
            "high signal-to-noise ratio to inform decisions or research."
        ),
    )
    follow_up_queries: list[str] = Field(
        ...,
        title="Follow-up Queries",
        description=(
            "Curated, insightful queries to deepen topic understanding. "
            "Questions should guide further research, uncover insights, or "
            "validate hypotheses. Each should be clear, specific, and "
            "data-aligned to ensure efficient and impactful subsequent "
            "investigations."
        ),
    )

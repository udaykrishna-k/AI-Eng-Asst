from pydantic import BaseModel, Field


class ConceptExplaination(BaseModel):
    concept: str = Field(description="Name of the technical concept")
    explanation: str = Field(description="A concise technical explanation")
    difficulty: str = Field(description="One of: Beginner, Intermediate, Advanced")
    related_topics: list[str] = Field(
        description="A list of related technical topics"
    )
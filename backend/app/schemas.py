from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class SourceType(str, Enum):
    text = "text"
    url = "url"


class IngestRequest(BaseModel):
    source_type: SourceType
    content: Optional[str] = Field(
        default=None, description="Required when source_type == 'text'. The raw note text."
    )
    url: Optional[str] = Field(
        default=None, description="Required when source_type == 'url'. Page will be fetched server-side."
    )
    title: Optional[str] = Field(default=None, max_length=200)

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("content cannot be blank")
        return v

    @model_validator(mode="after")
    def check_required_fields(self) -> "IngestRequest":
        if self.source_type == SourceType.text and not self.content:
            raise ValueError("content is required when source_type is 'text'")
        if self.source_type == SourceType.url and not self.url:
            raise ValueError("url is required when source_type is 'url'")
        if self.source_type == SourceType.url and self.url:
            if not (self.url.startswith("http://") or self.url.startswith("https://")):
                raise ValueError("url must start with http:// or https://")
        return self


class IngestResponse(BaseModel):
    id: str
    source_type: SourceType
    title: Optional[str]
    chunk_count: int
    created_at: datetime


# ---------- /items ----------

class ItemSummary(BaseModel):
    id: str
    source_type: SourceType
    title: Optional[str]
    source_url: Optional[str]
    chunk_count: int
    created_at: datetime
    content_preview: str


class ItemListResponse(BaseModel):
    items: list[ItemSummary]
    count: int


# ---------- /query ----------

class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question cannot be blank")
        return v


class SourceSnippet(BaseModel):
    item_id: str
    title: Optional[str]
    chunk_index: int
    chunk_text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
    retrieved_chunk_count: int


# ---------- Errors ----------

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

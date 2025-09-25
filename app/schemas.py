from pydantic import BaseModel
from typing import List, Optional


class IngestRequest(BaseModel):
    feature_id: str
    document_id: str
    document_text: str


class Relation(BaseModel):
    head: str
    relation: str
    tail: str


class RelationsOutput(BaseModel):
    relations: List[Relation]


class QueryRequest(BaseModel):
    query: str
    feature_id: Optional[str] = None
    top_k: int = 3


class QueryResponse(BaseModel):
    doc_ids: List[str]
    context: str

from pydantic import BaseModel
from typing import List


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
    top_k: int = 3


class QueryResponse(BaseModel):
    answer: str
    entities: List[str]
    graph_relations: List[dict]
    context: str

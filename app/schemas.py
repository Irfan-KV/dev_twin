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

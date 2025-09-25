from pydantic import BaseModel
from typing import List, Optional

class IngestRequest(BaseModel):
    feature_id: str
    document_id: str
    document_text: str

class Entity(BaseModel):
    name: str      # Human-readable identifier
    label: str     # Neo4j node label (Feature, Developer, Task, etc.)

class Relationship(BaseModel):
    from_entity: str       # Entity name (source node)
    to_entity: str         # Entity name (target node)
    type: str              # Relationship type (WORKED_ON, CONTRIBUTED_TO, etc.)
    explanation: str       # Optional reasoning/context

class KnowledgeGraphOutput(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]

class QueryRequest(BaseModel):
    query: str
    feature_id: Optional[str] = None
    top_k: int = 3

class QueryResponse(BaseModel):
    doc_ids: List[str]
    context: str

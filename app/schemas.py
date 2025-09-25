from pydantic import BaseModel
from typing import List

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
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    entities: List[str]
    graph_relations: List[dict]
    context: str

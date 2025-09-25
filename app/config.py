import os
from typing import List, Tuple


class Settings:
    openai_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_pass: str
    qdrant_collection: str
    embedding_model: str

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.qdrant_url = os.getenv("QDRANT_URL", "")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.neo4j_uri = os.getenv("NEO4J_URI", "")
        self.neo4j_user = os.getenv("NEO4J_USER", "")
        self.neo4j_pass = os.getenv("NEO4J_PASS", "")
        self.qdrant_collection = os.getenv("QDRANT_COLLECTION", "graph_rag_demo")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    def validate(self) -> List[str]:
        missing = [
            name
            for name, val in {
                "OPENAI_API_KEY": self.openai_api_key,
                "QDRANT_URL": self.qdrant_url,
                "QDRANT_API_KEY": self.qdrant_api_key,
                "NEO4J_URI": self.neo4j_uri,
                "NEO4J_USER": self.neo4j_user,
                "NEO4J_PASS": self.neo4j_pass,
            }.items()
            if not val
        ]
        return missing

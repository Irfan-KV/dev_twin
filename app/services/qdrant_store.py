import uuid
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

def ensure_collection(client: QdrantClient, collection: str) -> None:
    try:
        client.get_collection(
            collection)
    except Exception:
        client.recreate_collection(
            collection_name=collection,
            vectors_config=qmodels.VectorParams(
                size=1536, distance=qmodels.Distance.COSINE
            ),
             payload_schema={
        "feature_id": qmodels.PayloadSchemaType.KEYWORD}
        )


def upsert_chunks(
    client: QdrantClient,
    collection: str,
    vectors: List[List[float]],
    chunks: List[str],
    payload_base: Dict[str, str],
) -> None:
    client.upsert(
        collection_name=collection,
        points=[
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=v,
                payload={**payload_base, "chunk": c},
            )
            for v, c in zip(vectors, chunks)
        ],
    )

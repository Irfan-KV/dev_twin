from fastapi import FastAPI, HTTPException
from app.schemas import IngestRequest, QueryRequest, QueryResponse
from app.config import Settings
from app.services.text import chunk_text
from app.services.embeddings import embed_chunks
from app.services.qdrant_store import ensure_collection, upsert_chunks
from app.services.graph_store import create_driver, upsert_relations
from qdrant_client import QdrantClient


app = FastAPI(title="Dev Twin API")


@app.get("/")
def read_root() -> dict:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"health": "ok"}


@app.post("/ingest-data")
def ingest_data(req: IngestRequest) -> dict:
    settings = Settings()
    missing = settings.validate()
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing environment variables: {', '.join(missing)}",
        )

    qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    ensure_collection(qdrant, settings.qdrant_collection)

    chunks = chunk_text(req.document_text)
    vectors = embed_chunks(chunks, settings.embedding_model, settings.openai_api_key)
    upsert_chunks(
        qdrant,
        settings.qdrant_collection,
        vectors,
        chunks,
        {"feature_id": req.feature_id, "document_id": req.document_id},
    )

    driver = create_driver(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_pass)
    # upsert_document(driver, req.document_id, req.document_text, req.feature_id)

    from app.services.relations import extract_relations

    relations_iter = extract_relations(req.document_text, settings.openai_api_key)
    # upsert_relations(driver, relations_iter, req.document_id, req.feature_id)
    upsert_relations(driver, relations_iter)

    return {
        "status": "ingested",
        "feature_id": req.feature_id,
        "document_id": req.document_id,
        "chunks": len(chunks),
        "collection": settings.qdrant_collection,
    }


@app.post("/query", response_model=QueryResponse)
def run_query(req: QueryRequest) -> QueryResponse:
    settings = Settings()
    missing = settings.validate()
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing environment variables: {', '.join(missing)}",
        )

    from app.services.query import graph_rag_query

    qdrant = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    driver = create_driver(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_pass)

    answer, entities, graph_relations, context = graph_rag_query(
        question=req.query,
        top_k=req.top_k,
        openai_api_key=settings.openai_api_key,
        qdrant=qdrant,
        collection=settings.qdrant_collection,
        embedding_model=settings.embedding_model,
        neo_driver=driver,
    )

    return QueryResponse(
        answer=answer,
        entities=entities,
        graph_relations=graph_relations,
        context=context,
    )

from typing import List, Dict
from openai import OpenAI
from qdrant_client import QdrantClient
from app.services.embeddings import embed_chunks
from app.services.graph_store import fetch_relations_by_entities


def graph_rag_query(
    question: str,
    top_k: int,
    openai_api_key: str,
    qdrant: QdrantClient,
    collection: str,
    embedding_model: str,
    neo_driver,
) -> tuple[str, List[str], List[Dict[str, str]], str]:
    # 1) semantic retrieval from Qdrant
    emb = embed_chunks([question], model=embedding_model, api_key=openai_api_key)[0]
    hits = qdrant.search(collection_name=collection, query_vector=emb, limit=top_k)
    text_context = "\n".join([h.payload.get("chunk", "") for h in hits])

    # 2) extract entities using LLM
    client = OpenAI(api_key=openai_api_key)
    entity_prompt = (
        "Extract the key entities from the following question.\n"
        "Return a comma-separated list of entities.\n"
        f"Question: {question}"
    )
    entities_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": entity_prompt}],
    )
    entities_str = entities_resp.choices[0].message.content or ""
    entities = [e.strip() for e in entities_str.split(",") if e.strip()]

    # 3) query Neo4j relations
    graph_relations = fetch_relations_by_entities(neo_driver, entities)

    # 4) final answer
    final_prompt = (
        "Answer the question using the text context and knowledge graph.\n"
        f"Question: {question}\n\n"
        f"Text context:\n{text_context}\n\n"
        f"Graph relations:\n{graph_relations}\n"
    )
    ans = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
    )
    answer = ans.choices[0].message.content or ""

    return answer, entities, graph_relations, text_context

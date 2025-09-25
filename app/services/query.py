from typing import List, Dict
from openai import OpenAI
from qdrant_client import QdrantClient
from app.services.embeddings import embed_chunks
from app.services.graph_store import fetch_relations_by_entities, get_all_entity_labels


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
    all_labels = get_all_entity_labels(neo_driver)
    all_labels_str = ",".join(all_labels)
    entity_prompt = f"""
        You are an expert knowledge graph assistant.
        Given the following entity labels in Neo4j database:
        {all_labels_str}
        And the user question: "{question}"
        Identify which entities are relevant to answer the question.
        Only return entities that are present in the Neo4j database.
        Do not make up any entities.
        Return a comma-separated list of entities.
        """

    entities_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": entity_prompt}],
    )
    entities_str = entities_resp.choices[0].message.content or ""
    entities = [e.strip() for e in entities_str.split(",") if e.strip()]
    print(f"Entities: {entities}")

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

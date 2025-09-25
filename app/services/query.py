from typing import List, Dict, Optional
from openai import OpenAI
from qdrant_client import QdrantClient
from app.services.embeddings import embed_chunks
from app.services.graph_store import fetch_relations_by_entities, get_all_entity_labels
from qdrant_client.models import Filter, FieldCondition, MatchValue

def graph_rag_query(
    question: str,
    feature_id: Optional[str],
    top_k: int,
    openai_api_key: str,
    qdrant: QdrantClient,
    collection: str,
    embedding_model: str,
    neo_driver,
) -> tuple[str, List[str], List[Dict[str, str]], str]:
    # 1) semantic retrieval from Qdrant
    emb = embed_chunks([question], model=embedding_model, api_key=openai_api_key)[0]

    # query_filter = None
    # if feature_id:
    #     query_filter = {
    #     "must": [
    #         {"key": "feature_id", "match": {"value": feature_id}}
    #     ]
    # }

    # hits = qdrant.search(collection_name=collection, query_vector=emb, limit=top_k ,query_filter=query_filter)
    hits = qdrant.search(collection_name=collection, query_vector=emb, limit=top_k )
    text_context = "\n".join([h.payload.get("chunk", "") for h in hits])

    print("Payloads:", [h.payload.keys() for h in hits])

    chunk_doc_ids = list(
        {h.payload.get("document_id") for h in hits if h.payload.get("document_id")}
    )
    print("chunk_doc_ids", chunk_doc_ids)


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

     # 3b) filter relations using LLM
    filter_prompt = (
        "You are a knowledge graph assistant.\n"
        "Given a user question and a list of relations (triplets: source - relation - target, "
        "and their document ids) select only the relations that are directly relevant to answering the question.\n"
        "Return them as a JSON array of objects with keys: source, source_doc_id, relation, target, target_doc_id.\n\n"
        f"Question: {question}\n\n"
        f"Relations:\n{graph_relations}\n\n"
        "Relevant relations:"
    )

    filter_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": filter_prompt}],
        response_format={"type": "json_object"},  # ensures JSON parseable response
    )

    try:
        final_graph_relations = filter_resp.choices[0].message.parsed["Relevant relations"]
    except Exception:
        # fallback: just keep raw relations if parsing fails
        final_graph_relations = graph_relations

    doc_ids = list(
            set(
                [rel["source_doc_id"] for rel in final_graph_relations if rel.get("source_doc_id")]
                + [rel["target_doc_id"] for rel in final_graph_relations if rel.get("target_doc_id")]
            )
        )
    print("doc_ids",doc_ids)

    all_doc_ids = list(set(doc_ids) | set(chunk_doc_ids))
    # all_doc_ids = list(set(doc_ids) - set(chunk_doc_ids))
    print("All doc ids:", all_doc_ids)


    return all_doc_ids, text_context

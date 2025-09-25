from typing import List, Dict
from neo4j import GraphDatabase, Driver
from app.schemas import KnowledgeGraphOutput


def create_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


def get_all_entity_labels(driver: Driver) -> List[str]:
    with driver.session() as session:
        labels = [record["label"] for record in session.run("CALL db.labels()")]
    return labels


def fetch_relations_by_entities(
    driver: Driver, entities: List[str]
) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    with driver.session() as session:
        for ent in entities:
            label_safe = safe_label(ent)
            query = (
                f"MATCH (n:`{label_safe}`) "
                "OPTIONAL MATCH (m)-[r]->(n) "
                "RETURN n.name AS entity, m.name AS related_entity, type(r) AS relation, r.explanation AS reason"
            )
            for rec in session.run(query):
                results.append(
                    {
                        "entity": rec.get("entity"),
                        "related_entity": rec.get("related_entity"),
                        "relation": rec.get("relation"),
                        "reason": rec.get("reason"),
                    }
                )
    return results


def safe_label(name: str) -> str:
    return name.replace("`", "").replace(" ", "_").replace("-", "_").replace("/", "_")


def ingest_kg_to_neo4j_structured(
    driver: Driver, kg_output: KnowledgeGraphOutput
) -> None:
    with driver.session() as session:
        for entity in kg_output.entities:
            label_safe = safe_label(entity.name)
            session.run(
                f"MERGE (n:`{label_safe}` {{name: $name}})",
                name=entity.name,
            )
        for rel in kg_output.relationships:
            from_label = safe_label(rel.from_entity)
            to_label = safe_label(rel.to_entity)
            rel_type = safe_label(rel.type)
            session.run(
                f"""
                MATCH (a:`{from_label}` {{name: $from_name}})
                MATCH (b:`{to_label}` {{name: $to_name}})
                MERGE (a)-[r:`{rel_type}`]->(b)
                SET r.explanation = $explanation
                """,
                from_name=rel.from_entity,
                to_name=rel.to_entity,
                explanation=rel.explanation,
            )

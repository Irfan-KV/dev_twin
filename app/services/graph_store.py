from typing import Iterable, List, Dict
from neo4j import GraphDatabase, Driver
from app.schemas import KnowledgeGraphOutput


def create_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


def upsert_relations(
    driver: Driver,
    relations: Iterable[tuple[str, str, str]],
    document_id: str,
    feature_id: str,
) -> None:
    with driver.session() as s:
        for head, relation, tail in relations:
            rel_clean = relation.replace(" ", "_")
            s.execute_write(
                lambda tx, a=head, r=rel_clean, b=tail, d=document_id, f=feature_id: tx.run(
                    "MERGE (x:Entity {name:$a}) "
                    "SET x.document_id=$d, x.feature_id=$f "
                    "MERGE (y:Entity {name:$b}) "
                    "SET y.document_id=$d, y.feature_id=$f "
                    f"MERGE (x)-[rel:{r}]->(y) "
                    "SET rel.document_id=$d, rel.feature_id=$f",
                    a=a,
                    b=b,
                    d=d,
                    f=f,
                )
            )


def get_all_entity_labels(driver: Driver) -> List[str]:
    with driver.session() as session:
        labels = [record["label"] for record in session.run("CALL db.labels()")]
    return labels


def fetch_relations_by_entities(
    driver: Driver, entities: List[str]
) -> List[Dict[str, str]]:
    query = (
        "MATCH (e:Entity)-[r]->(t:Entity) "
        "WHERE e.name IN $entities OR t.name IN $entities "
        "RETURN e.name AS source, type(r) AS relation, t.name AS target"
    )
    with driver.session() as session:
        return session.read_transaction(
            lambda tx: [
                {
                    "source": rec["source"],
                    "relation": rec["relation"],
                    "target": rec["target"],
                }
                for rec in tx.run(query, entities=entities)
            ]
        )


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

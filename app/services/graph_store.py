from typing import Iterable
from neo4j import GraphDatabase, Driver


def create_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


def upsert_document(
    driver: Driver, document_id: str, text: str, feature_id: str
) -> None:
    with driver.session() as s:
        s.execute_write(
            lambda tx: tx.run(
                "MERGE (d:Document {id:$id}) SET d.text=$text, d.feature_id=$fid",
                id=document_id,
                text=text,
                fid=feature_id,
            )
        )


def upsert_relations(driver: Driver, relations: Iterable[tuple[str, str, str]]) -> None:
    with driver.session() as s:
        for head, relation, tail in relations:
            rel_clean = relation.replace(" ", "_")
            s.execute_write(
                lambda tx, a=head, r=rel_clean, b=tail: tx.run(
                    "MERGE (x:Entity {name:$a}) "
                    "MERGE (y:Entity {name:$b}) "
                    f"MERGE (x)-[r:{r}]->(y)",
                    a=a,
                    b=b,
                )
            )

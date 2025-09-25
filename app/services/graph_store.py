from typing import Iterable, List, Dict
from neo4j import GraphDatabase, Driver


def create_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


# def upsert_document(
#     driver: Driver, document_id: str, text: str, feature_id: str
# ) -> None:
#     with driver.session() as s:
#         s.execute_write(
#             lambda tx: tx.run(
#                 "MERGE (d:Document {id:$id}) SET d.text=$text, d.feature_id=$fid",
#                 id=document_id,
#                 text=text,
#                 fid=feature_id,
#             )
#         )


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


def fetch_relations_by_entities(
    driver: Driver, entities: List[str]
) -> List[Dict[str, str]]:
    query = (
        "MATCH (e:Entity)-[r]->(t:Entity) "
        "WHERE e.name IN $entities OR t.name IN $entities "
        "RETURN e.name AS source, e.document_id AS source_doc_id, type(r) AS relation, t.name AS target, t.document_id AS target_doc_id"
    )
    with driver.session() as session:
        return session.execute_read(
            lambda tx: [
                {
                    "source": rec["source"],
                    "source_doc_id": rec["source_doc_id"],
                    "relation": rec["relation"],
                    "target": rec["target"],
                    "target_doc_id": rec["target_doc_id"],
                }
                for rec in tx.run(query, entities=entities)
            ]
        )

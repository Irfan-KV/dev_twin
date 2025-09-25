from typing import List
from openai import OpenAI


def embed_chunks(chunks: List[str], model: str, api_key: str) -> List[List[float]]:
    client = OpenAI(api_key=api_key)
    resp = client.embeddings.create(input=chunks, model=model)
    return [d.embedding for d in resp.data]

from typing import List


def chunk_text(text: str, size: int = 500, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start : start + size])
        if chunk:
            chunks.append(chunk)
        start += max(1, size - overlap)
    return chunks

from sentence_transformers import CrossEncoder

reranker = None


def load_model():
    global reranker
    if reranker is None:
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query, passages, top_k=5):
    """Original function, unchanged — operates on plain text passages."""
    load_model()
    pairs = [[query, p] for p in passages]
    scores = reranker.predict(pairs)
    scored = list(zip(passages, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in scored[:top_k]]


def rerank_chunks(query, chunks, top_k=5):
    """
    Same idea as rerank(), but operates on chunk dicts (with "text", "source",
    "page", "location", etc.) and returns the reranked dicts intact — so
    citation metadata survives reranking instead of being discarded.
    """
    load_model()
    if not chunks:
        return []
    pairs = [[query, c["text"]] for c in chunks]
    scores = reranker.predict(pairs)
    scored = list(zip(chunks, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _score in scored[:top_k]]

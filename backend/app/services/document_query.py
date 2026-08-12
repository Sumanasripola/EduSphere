"""
The pgvector-backed counterpart to the old FAISS query_rag() — retrieves
across any document type (PDF/DOCX/XLSX/CSV/Image), scoped to a specific
user (and optionally a specific set of their documents), reranks, and
generates a cited answer.
"""
import re
from collections import defaultdict

from app.services.embedding_service import embed
from app.services.reranker import rerank_chunks
from app.services.llm_service import generate_answer
from app.services.excel_service import create_excel
from app.vectorstore.pgvector_store import search

RETRIEVAL_K = 40
RERANK_TOP_K = 15


def extract_markdown_table(answer: str):
    lines = answer.split("\n")
    table_lines = [l.strip() for l in lines if l.strip().startswith("|") and "|" in l]

    if len(table_lines) < 2:
        return None, None

    rows = []
    for line in table_lines:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        rows.append(cols)

    if len(rows) > 1 and all(re.fullmatch(r"[-: ]+", c) for c in rows[1]):
        rows.pop(1)

    if len(rows) < 2:
        return None, None

    return rows[1:], rows[0]


def _location_label(chunk: dict) -> str:
    """A chunk's citation label: a real page for PDFs, or the loader's
    location string (heading / row range / OCR) for everything else."""
    if chunk.get("page"):
        return f"page {chunk['page']}"
    return chunk.get("location") or "unknown location"


def build_citations(used_chunks: list) -> list:
    by_source = defaultdict(set)
    for c in used_chunks:
        by_source[c["source"]].add(_location_label(c))

    return [
        {"source": source, "locations": sorted(locations)}
        for source, locations in by_source.items()
    ]


def answer_question(question: str, user_id: str, document_ids: list = None) -> dict:
    query_vec = embed([question])[0]

    candidates = search(query_vec, user_id, document_ids=document_ids, k=RETRIEVAL_K)

    if not candidates:
        return {
            "answer": "No indexed documents found to answer from. Upload something first.",
            "citations": [],
            "excel": None,
        }

    top_chunks = rerank_chunks(question, candidates, top_k=RERANK_TOP_K)

    # Deduplicate near-identical chunks by (source, first-100-chars) before
    # building context, same defensive pattern as the original pipeline.
    seen = set()
    context_parts = []
    used_chunks = []
    for c in top_chunks:
        key = (c["source"], c["text"][:100])
        if key in seen:
            continue
        seen.add(key)
        context_parts.append(f"[{c['source']} — {_location_label(c)}]\n{c['text']}")
        used_chunks.append(c)

    context = "\n\n".join(context_parts)
    is_comparison = bool(document_ids and len(document_ids) > 1)

    answer = generate_answer(question, context, is_comparison=is_comparison)

    excel_path = None
    rows, header = extract_markdown_table(answer)
    if rows and header:
        excel_path = create_excel(rows, header)

    citations = build_citations(used_chunks)

    return {"answer": answer, "citations": citations, "excel": excel_path}

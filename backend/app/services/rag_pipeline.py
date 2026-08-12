from app.services.pdf_parser import (
    extract_text_images,
    render_page_region,
    find_figure_regions,
    scan_page_for_figure_label,
    get_pdf_page_count,
)
from app.services.embedding_service import embed
from app.vectorstore.faiss_store import add_vectors, search
from app.utils.chunking import chunk_text
from app.services.llm_service import generate_answer
from app.services.reranker import rerank
from app.services.excel_service import create_excel

import os
from collections import defaultdict
import re

IMAGE_DIR = "storage/images"
UPLOAD_DIR = "storage/uploads"
os.makedirs(IMAGE_DIR, exist_ok=True)


# =============================================================================
# 📄  PROCESS DOCUMENT  (upload time — text only, fast)
# =============================================================================
def process_document(pdf_path: str):
    print("Processing:", pdf_path)

    pdf_name = os.path.basename(pdf_path)
    texts, _ = extract_text_images(pdf_path)

    all_chunks    = []
    text_metadata = []

    for page_num, page_text in enumerate(texts, start=1):
        chunks = chunk_text(page_text)
        for chunk in chunks:
            all_chunks.append(chunk)
            text_metadata.append({
                "type":   "text",
                "text":   chunk,
                "source": pdf_name,
                "page":   page_num,
            })

    if all_chunks:
        text_vectors = embed(all_chunks)
        add_vectors(text_vectors, text_metadata)

    print(f"✅ Stored {len(all_chunks)} text chunks (images deferred to query time)")


# =============================================================================
# ⚖  BALANCED RETRIEVAL
# =============================================================================
def get_balanced_chunks(chunks, selected_pdfs, max_per_pdf=10):
    grouped = defaultdict(list)
    for c in chunks:
        grouped[c["source"]].append(c)

    balanced = []
    for pdf in selected_pdfs:
        balanced.extend(grouped.get(pdf, [])[:max_per_pdf])
    return balanced


# =============================================================================
# 🔥  TABLE EXTRACTION FROM MARKDOWN
# =============================================================================
def extract_markdown_table(answer: str):
    lines       = answer.split("\n")
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


# =============================================================================
# 🔍  BUILD CITATIONS
# =============================================================================
def build_citations(used_chunks: list) -> list:
    by_source = defaultdict(set)
    for c in used_chunks:
        by_source[c["source"]].add(c["page"])

    return [
        {"source": source, "pages": sorted(pages)}
        for source, pages in by_source.items()
    ]


# =============================================================================
# 🖼  ON-DEMAND IMAGE EXTRACTION  (query time)
# =============================================================================
def extract_images_for_pages(pdf_name: str, page_numbers: list):
    """
    Render figure regions found on the given pages.
    Each page is processed exactly once.
    """
    pdf_path = os.path.join(UPLOAD_DIR, pdf_name)
    if not os.path.exists(pdf_path):
        print(f"PDF not found on disk: {pdf_path}")
        return []

    rendered   = []
    seen_pages = set()

    for page_num in page_numbers:
        if page_num in seen_pages:
            continue
        seen_pages.add(page_num)

        figure_rects = find_figure_regions(pdf_path, page_num)

        if figure_rects:
            for rect in figure_rects:
                filename = render_page_region(pdf_path, page_num, rect=rect, scale=2.0)
                if filename:
                    rendered.append({
                        "image_path": filename,
                        "page":       page_num,
                        "source":     pdf_name,
                        "caption":    f"Figure from page {page_num}",
                    })

    return rendered


# =============================================================================
# 🔍  FIND FIGURE PAGE — SCANS THE ENTIRE PDF
# =============================================================================
def find_figure_page_in_pdf(pdf_name: str, fig_num: str) -> list:
    """
    Scan EVERY page of the PDF for "Figure N" / "Fig. N" label.

    This is the critical fix: previously we only scanned ±1 around the
    retrieved chunk pages, which missed figures on completely different pages.
    Now we do a full scan so "give me figure 2" always finds the right page
    regardless of which pages the text retrieval returned.

    Returns:
        Sorted list of 1-based page numbers that contain the label.
        Returns [] if nothing found.
    """
    pdf_path = os.path.join(UPLOAD_DIR, pdf_name)
    if not os.path.exists(pdf_path):
        print(f"PDF not found on disk: {pdf_path}")
        return []

    total_pages = get_pdf_page_count(pdf_path)
    if total_pages == 0:
        return []

    matched = []
    for page_num in range(1, total_pages + 1):
        if scan_page_for_figure_label(pdf_path, page_num, fig_num):
            matched.append(page_num)

    print(f"Figure {fig_num} label found on pages: {matched}")
    return matched


# =============================================================================
# 🔍  QUERY RAG
# =============================================================================

IMAGE_KEYWORDS = {
    "image", "figure", "fig", "diagram", "picture", "chart",
    "graph", "plot", "illustration", "show", "display", "visual",
    "render", "get", "give", "fetch", "extract", "see", "view",
}

TABLE_KEYWORDS = {
    "table", "compare", "comparison", "performance",
    "metrics", "statistics", "results", "scores",
}


def _is_image_request(question_lower: str) -> bool:
    words = set(re.findall(r"\w+", question_lower))
    return bool(words & IMAGE_KEYWORDS)


def _is_table_request(question_lower: str) -> bool:
    words = set(re.findall(r"\w+", question_lower))
    return bool(words & TABLE_KEYWORDS)


def query_rag(question: str, selected_pdfs: list):

    q_vector       = embed([question])[0]
    question_lower = question.lower()

    is_image_query = _is_image_request(question_lower)
    is_table_query = _is_table_request(question_lower)

    # Detect "figure 2", "fig 2", "fig. 2", "Figure2"
    specific_figure_match = re.search(
        r"\b(?:figure|fig\.?)\s*(\d+)\b", question_lower
    )
    specific_fig_num = specific_figure_match.group(1) if specific_figure_match else None

    # ── VECTOR SEARCH ────────────────────────────────────────────
    k          = 400 if (is_table_query or is_image_query) else 200
    candidates = search(q_vector, k=k)
    filtered   = [c for c in candidates if c["source"] in selected_pdfs]

    if not filtered:
        return {
            "answer":    "No relevant content found.",
            "citations": [],
            "excel":     None,
            "images":    [],
        }

    # ── TEXT PIPELINE ────────────────────────────────────────────
    balanced    = get_balanced_chunks(filtered, selected_pdfs)
    texts_list  = [c["text"] for c in balanced]
    top_k       = 25 if is_table_query else 15
    best_chunks = rerank(question, texts_list, top_k=top_k)

    context     = ""
    used_chunks = []
    seen        = set()

    for c in balanced:
        if c["text"] in best_chunks:
            key = (c["source"], c["text"][:120])
            if key not in seen:
                context += c["text"] + "\n\n"
                used_chunks.append(c)
                seen.add(key)

    # ── LLM ──────────────────────────────────────────────────────
    answer = generate_answer(question, context, len(selected_pdfs) > 1)

    # ── TABLE → EXCEL ─────────────────────────────────────────────
    excel_file  = None
    table_lines = [l for l in answer.split("\n") if l.strip().startswith("|")]
    table_data, columns = extract_markdown_table("\n".join(table_lines))
    if table_data:
        excel_file = create_excel(table_data, columns)

    # ── CITATIONS ─────────────────────────────────────────────────
    citations = build_citations(used_chunks)

    # ── ON-DEMAND IMAGE EXTRACTION ────────────────────────────────
    images = []

    if is_image_query:
        # Group chunk pages by PDF source
        pages_by_pdf = defaultdict(set)
        for c in used_chunks:
            pages_by_pdf[c["source"]].add(c["page"])

        # Make sure every selected PDF is included even if no chunks matched
        for pdf in selected_pdfs:
            if pdf not in pages_by_pdf:
                pages_by_pdf[pdf] = set()

        for pdf_name, page_set in pages_by_pdf.items():

            if specific_fig_num:
                # ✅ THE FIX: scan the ENTIRE PDF for the figure label.
                # Previously we only looked at ±1 of chunk pages, which missed
                # figures on pages the text retrieval didn't return (e.g. Figure 2
                # on p.3 when chunks came from p.7, p.12, p.14, p.15).
                target_pages = find_figure_page_in_pdf(pdf_name, specific_fig_num)

                if not target_pages:
                    # Nothing found by label scan — fall back to chunk pages
                    print(f"No label match for Figure {specific_fig_num}, falling back to chunk pages")
                    target_pages = sorted(page_set)
            else:
                # No specific figure requested — use chunk pages directly
                target_pages = sorted(page_set)

            imgs = extract_images_for_pages(pdf_name, target_pages)
            images.extend(imgs)

        # Deduplicate by rendered filename
        seen_paths = set()
        deduped    = []
        for img in images:
            if img["image_path"] not in seen_paths:
                seen_paths.add(img["image_path"])
                deduped.append(img)

        images = deduped[:3]

    return {
        "answer":    answer,
        "citations": citations,
        "excel":     excel_file,
        "images":    images,
    }
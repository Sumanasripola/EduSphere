"""
The single entry point for turning an uploaded file into searchable
chunks in Postgres/pgvector, regardless of its format.

Flow: detect type -> load -> chunk (where needed) -> embed -> store.
"""
import os

from app.utils.chunking import chunk_text
from app.services.embedding_service import embed
from app.services.loaders.pdf_loader import load_pdf
from app.services.loaders.docx_loader import load_docx
from app.services.loaders.xlsx_loader import load_xlsx
from app.services.loaders.csv_loader import load_csv
from app.services.loaders.image_loader import load_image
from app.repositories.documents import create_document, update_document_status
from app.vectorstore.pgvector_store import add_chunks

SUPPORTED_TYPES = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".csv": "csv",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
}

# Formats whose loader returns raw prose sections that still need to be
# split into embedding-sized pieces. XLSX/CSV are already correctly
# row-chunked by their loaders and should NOT be re-chunked by word count
# — that would break apart the "Row N: col=val, ..." structure.
NEEDS_WORD_CHUNKING = {"pdf", "docx", "image"}


def detect_doc_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {ext}")
    return SUPPORTED_TYPES[ext]


def process_document(file_path: str, filename: str, user_id: str) -> dict:
    """
    Processes any supported file end-to-end: extracts, chunks, embeds,
    and indexes it into pgvector, scoped to user_id. Returns the created
    document's id and final status.
    """
    doc_type = detect_doc_type(filename)
    document_id = create_document(user_id, filename, doc_type, status="processing")

    try:
        if doc_type == "pdf":
            sections = load_pdf(file_path)
        elif doc_type == "docx":
            sections = load_docx(file_path)
        elif doc_type == "xlsx":
            sections = load_xlsx(file_path)
        elif doc_type == "csv":
            sections = load_csv(file_path)
        elif doc_type == "image":
            sections = load_image(file_path)
        else:
            raise ValueError(f"No loader wired for type: {doc_type}")

        chunks = []
        for section in sections:
            location = section.get("location")
            page = section.get("page")  # only PDFs set a real integer page

            if doc_type in NEEDS_WORD_CHUNKING:
                for piece in chunk_text(section["text"]):
                    chunks.append({"text": piece, "page": page, "location": location})
            else:
                chunks.append({"text": section["text"], "page": page, "location": location})

        if not chunks:
            update_document_status(document_id, "failed")
            return {"document_id": document_id, "status": "failed", "chunks_indexed": 0,
                     "reason": "No extractable text found in file."}

        vectors = embed([c["text"] for c in chunks])
        add_chunks(document_id, user_id, chunks, vectors)

        update_document_status(document_id, "ready")
        return {"document_id": document_id, "status": "ready", "chunks_indexed": len(chunks)}

    except Exception as e:
        update_document_status(document_id, "failed")
        return {"document_id": document_id, "status": "failed", "chunks_indexed": 0, "reason": str(e)}

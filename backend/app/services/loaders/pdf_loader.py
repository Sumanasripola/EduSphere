"""
Wraps the existing extract_text_images() from pdf_parser.py into the same
normalized {"text", "location"} shape the other loaders produce, so the
pipeline can treat every format identically from this point on.
"""
from app.services.pdf_parser import extract_text_images


def load_pdf(file_path: str):
    texts, _images = extract_text_images(file_path)

    chunks = []
    for page_num, page_text in enumerate(texts, start=1):
        if page_text and page_text.strip():
            chunks.append({"text": page_text, "location": f"page {page_num}", "page": page_num})

    return chunks

"""
Loads a .docx file into the same normalized shape every other loader
produces: a list of {"text": str, "location": str} dicts.

Unlike a PDF, a Word document has no fixed "page" concept until it's
printed — so instead of a page number, each chunk's location is the
nearest heading above it (e.g. "Chapter 2 > Data Collection"). This is
what shows up in citations for DOCX sources.
"""
from docx import Document


def load_docx(file_path: str):
    doc = Document(file_path)

    sections = []  # list of {"heading": str, "text": str}
    current_heading = "Document start"
    current_text_parts = []

    def flush():
        text = "\n".join(current_text_parts).strip()
        if text:
            sections.append({"heading": current_heading, "text": text})

    for para in doc.paragraphs:
        style = (para.style.name or "").lower()
        text = para.text.strip()

        if not text:
            continue

        if style.startswith("heading") or style == "title":
            flush()
            current_heading = text
            current_text_parts = []
        else:
            current_text_parts.append(text)

    flush()

    # Also pull any text sitting inside tables (common in course handouts)
    for table_idx, table in enumerate(doc.tables):
        rows_text = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                rows_text.append(" | ".join(cells))
        if rows_text:
            sections.append({
                "heading": f"Table {table_idx + 1}",
                "text": "\n".join(rows_text),
            })

    if not sections:
        return []

    return [{"text": s["text"], "location": s["heading"]} for s in sections]

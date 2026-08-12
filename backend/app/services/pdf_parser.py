import fitz
import re
import os
import uuid

IMAGE_DIR = "storage/images"
os.makedirs(IMAGE_DIR, exist_ok=True)


# =============================================================================
# 📄  UPLOAD TIME — text only, images skipped
# =============================================================================
def extract_text_images(pdf_path: str):
    doc   = fitz.open(pdf_path)
    texts = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            texts.append(text)
    doc.close()
    return texts, []          # images always empty


# =============================================================================
# 📏  GET TOTAL PAGE COUNT
# =============================================================================
def get_pdf_page_count(pdf_path: str) -> int:
    """Return total number of pages in the PDF."""
    try:
        doc   = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        print("get_pdf_page_count error:", e)
        return 0


# =============================================================================
# 🔍  SCAN ONE PAGE FOR A FIGURE LABEL
# =============================================================================
def scan_page_for_figure_label(pdf_path: str, page_num: int, fig_num: str) -> bool:
    """
    Returns True if the page text contains a reference to the given figure number.
    Matches: "Figure 2", "Figure2", "Fig 2", "Fig. 2", "FIG. 2" (case-insensitive).
    Also matches caption-style text like "Figure 2:" or "Figure 2."

    Args:
        pdf_path : path to the PDF on disk
        page_num : 1-based page number
        fig_num  : figure number as string, e.g. "2"
    """
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            doc.close()
            return False

        page = doc[page_num - 1]
        text = page.get_text()
        doc.close()

        # Matches: Figure 2, Figure2, Fig 2, Fig. 2, FIG 2 — optionally followed by : or .
        pattern = rf"\bfig(?:ure)?\.?\s*{re.escape(fig_num)}\b"
        return bool(re.search(pattern, text, re.IGNORECASE))

    except Exception as e:
        print(f"scan_page_for_figure_label error (page {page_num}):", e)
        return False


# =============================================================================
# 🖼  RENDER A REGION OF A PAGE AS A HIGH-RES PNG
# =============================================================================
def render_page_region(pdf_path: str, page_num: int, rect=None, scale: float = 2.0):
    """
    Render a region of a PDF page as a PNG.

    Args:
        rect  : fitz.Rect to crop, or None for the full page
        scale : 2.0 = 144 dpi — crisp on retina screens
    """
    try:
        doc  = fitz.open(pdf_path)
        page = doc[page_num - 1]
        mat  = fitz.Matrix(scale, scale)

        if rect:
            padding = 20
            padded  = fitz.Rect(
                max(0,            rect.x0 - padding),
                max(0,            rect.y0 - padding),
                min(page.rect.x1, rect.x1 + padding),
                min(page.rect.y1, rect.y1 + padding),
            )
            clip = padded
        else:
            clip = page.rect

        pix      = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(IMAGE_DIR, filename)
        pix.save(filepath)
        doc.close()
        return filename

    except Exception as e:
        print(f"render_page_region error (page {page_num}):", e)
        return None


# =============================================================================
# 🔍  DETECT AND MERGE FIGURE BOUNDING BOXES ON A PAGE
# =============================================================================
def find_figure_regions(pdf_path: str, page_num: int, min_size: int = 80):
    """
    Detect embedded image positions on a page and merge overlapping bboxes.
    Returns list of fitz.Rect — one per distinct figure region.
    """
    try:
        doc  = fitz.open(pdf_path)
        page = doc[page_num - 1]

        raw_rects  = []
        seen_xrefs = set()

        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            for r in page.get_image_rects(xref):
                if r.width >= min_size and r.height >= min_size:
                    raw_rects.append(fitz.Rect(r))

        doc.close()

        if not raw_rects:
            return []

        merged = _merge_rects(raw_rects, padding=25)
        return [r for r in merged if r.width >= min_size and r.height >= min_size]

    except Exception as e:
        print(f"find_figure_regions error (page {page_num}):", e)
        return []


def _merge_rects(rects, padding=25):
    """Iteratively merge overlapping or nearby rects until stable."""
    merged  = [fitz.Rect(r) for r in rects]
    changed = True

    while changed:
        changed = False
        result  = []

        while merged:
            base = merged.pop(0)
            expanded = fitz.Rect(
                base.x0 - padding, base.y0 - padding,
                base.x1 + padding, base.y1 + padding,
            )
            remaining = []

            for other in merged:
                if expanded.intersects(other):
                    base = fitz.Rect(
                        min(base.x0, other.x0), min(base.y0, other.y0),
                        max(base.x1, other.x1), max(base.y1, other.y1),
                    )
                    expanded = fitz.Rect(
                        base.x0 - padding, base.y0 - padding,
                        base.x1 + padding, base.y1 + padding,
                    )
                    changed = True
                else:
                    remaining.append(other)

            result.append(base)
            merged = remaining

        merged = result

    return merged
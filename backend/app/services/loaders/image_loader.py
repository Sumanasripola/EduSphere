"""
Loads an image file into normalized {"text", "location"} chunks.

Two paths, tried in order:
1. OCR (pytesseract) — for scanned notes, screenshotted slides, photos of
   a whiteboard, etc. where the "content" IS text.
2. If OCR finds little or no text, fall back to BLIP image captioning —
   for diagrams, charts, or photos where there's no text to read, but a
   one-line description is still better than nothing in search results.
   (This is the same BLIP setup that already existed in image_captioner.py
   but was never wired into anything — this finally uses it.)
"""
import pytesseract
from PIL import Image

MIN_OCR_CHARS = 20  # below this, treat OCR as "found nothing useful"


def load_image(file_path: str):
    img = Image.open(file_path)

    ocr_text = pytesseract.image_to_string(img).strip()

    if len(ocr_text) >= MIN_OCR_CHARS:
        return [{"text": ocr_text, "location": "OCR text"}]

    # Fall back to captioning. Imported lazily so pytesseract-only use
    # cases don't pay the cost of loading the BLIP model.
    try:
        from app.services.image_captioner import caption_image
        caption = caption_image(file_path)
        if caption:
            return [{"text": caption, "location": "Image caption"}]
    except Exception:
        pass

    return []

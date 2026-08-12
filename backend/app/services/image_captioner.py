from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import re

processor = None
model = None


def load_model():
    global processor, model

    if processor is None:
        processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

    if model is None:
        model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )


def caption_image(image_bytes: bytes) -> str:
    """
    Generate a descriptive semantic caption for an image using BLIP.
    Falls back to a generic label on failure.
    """
    try:
        load_model()

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Resize very large images to speed up inference
        max_side = 800
        w, h = image.size
        if max(w, h) > max_side:
            scale = max_side / max(w, h)
            image = image.resize(
                (int(w * scale), int(h * scale)),
                Image.LANCZOS
            )

        # Conditional captioning: give BLIP a starting hint
        text = "a diagram of"
        inputs = processor(image, text, return_tensors="pt")
        output = model.generate(
            **inputs,
            max_new_tokens=60,
            num_beams=4,
            early_stopping=True
        )
        caption = processor.decode(output[0], skip_special_tokens=True)

        # Clean up the hint prefix if echoed back
        caption = re.sub(r"^a diagram of\s*", "", caption, flags=re.IGNORECASE).strip()

        if not caption:
            return "figure"

        return caption

    except Exception as e:
        print("Caption error:", e)
        return "figure"
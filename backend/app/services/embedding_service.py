from sentence_transformers import SentenceTransformer

model = None

def load_model():

    global model

    if model is None:

        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

def embed(texts):

    load_model()

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False
    )

    return embeddings
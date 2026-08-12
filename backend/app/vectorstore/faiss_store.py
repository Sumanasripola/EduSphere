import faiss
import numpy as np
import pickle
import os
from app.config import FAISS_INDEX_PATH, METADATA_PATH

dimension = 384  # for MiniLM

# load or create index
if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
else:
    index = faiss.IndexFlatL2(dimension)

# load metadata
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
else:
    metadata = []


def add_vectors(vectors, new_metadata):

    global metadata

    vectors = np.array(vectors).astype("float32")

    index.add(vectors)

    metadata.extend(new_metadata)

    # save
    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)


def search(query_vector, k=20):

    query_vector = np.array([query_vector]).astype("float32")

    distances, indices = index.search(query_vector, k)

    results = []

    for i in indices[0]:
        if i < len(metadata):
            results.append(metadata[i])

    return results
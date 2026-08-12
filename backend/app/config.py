import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

UPLOAD_DIR = "storage/uploads"
IMAGE_DIR = "storage/images"

FAISS_INDEX_PATH = "vector_db/faiss.index"
METADATA_PATH = "vector_db/metadata.pkl"
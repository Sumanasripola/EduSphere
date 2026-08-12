from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # ✅ FIXED POSITION

from app.api import upload, query, auth, chat

app = FastAPI(
    title="Multimodal PDF RAG",
    version="1.0"
)

# ✅ STATIC FILES (ORDER FIXED)
app.mount("/generated_excels", StaticFiles(directory="generated_excels"), name="excels")
app.mount("/images", StaticFiles(directory="storage/images"), name="images")

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def health():
    return {"status": "running"}
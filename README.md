# InsightRAG – Multimodal Document Intelligence System

InsightRAG is an AI-powered platform that allows users to upload multiple PDF documents and interact with them through intelligent, context-aware chat sessions. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to generate accurate answers grounded in document content.

---

## Features

- Upload and process multiple PDFs
- Create multiple chat sessions, each tied to selected PDFs
- Semantic search using FAISS vector embeddings
- Context-aware Q&A using RAG with intent detection
- Cross-encoder reranking for improved answer accuracy
- Image extraction from PDFs with caption-based retrieval
- Auto-generates downloadable Excel files from tabular answers
- Balanced multi-PDF retrieval to prevent one document dominating answers

---

## How It Works

1. User uploads one or more PDFs
2. PDFs are parsed to extract text and images
3. Text is split into overlapping chunks with sentence-aware boundaries
4. Each chunk is embedded using the BGE (`BAAI/bge-small-en-v1.5`) model
5. Embeddings are stored in a FAISS flat L2 vector index
6. When a question is asked:
   - Query intent is detected (table, image, comparison, or general)
   - Relevant chunks are retrieved from FAISS
   - Chunks are balanced across selected PDFs
   - Top chunks are reranked using a CrossEncoder model
   - Context is passed to Groq (Llama-3.3-70b) for answer generation
   - If the answer contains a markdown table, it is auto-exported to Excel

---

## Project Structure

### Backend (FastAPI)

```
backend/
│
├── app/
│   ├── api/
│   │   ├── upload.py              # Upload PDF endpoint
│   │   └── query.py               # Ask question endpoint
│   │
│   ├── services/
│   │   ├── rag_pipeline.py        # Main RAG workflow
│   │   ├── pdf_parser.py          # Extract text + images (PyMuPDF)
│   │   ├── embedding_service.py   # BGE embeddings
│   │   ├── llm_service.py         # Groq Llama-3 integration
│   │   ├── reranker.py            # CrossEncoder reranking
│   │   ├── excel_service.py       # Markdown table → Excel export
│   │   └── image_captioner.py     # BLIP image captioning
│   │
│   ├── vectorstore/
│   │   └── faiss_store.py         # FAISS index + metadata store
│   │
│   ├── utils/
│   │   ├── chunking.py            # Sentence-aware overlapping chunker
│   │   └── file_utils.py          # Upload file handling
│   │
│   ├── models/
│   │   ├── request_models.py      # QueryRequest (question + pdfs)
│   │   └── response_models.py     # QueryResponse with images + excel
│   │
│   ├── config.py                  # Env vars and paths
│   └── main.py                    # FastAPI app entry point
│
├── storage/
│   ├── uploads/                   # Uploaded PDFs
│   └── images/                    # Extracted PDF images
├── vector_db/                     # FAISS index and metadata
├── generated_excels/              # Auto-generated Excel files
└── run.py                         # Starts Uvicorn server
```

### Frontend (React + Vite)

```
insightRAG-frontend/
│
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx      # Chat input + message rendering
│   │   ├── MessageBubble.jsx      # User and AI message bubbles
│   │   ├── PDFUploader.jsx        # Drag-and-drop PDF upload
│   │   ├── Navbar.jsx             # Top navigation bar
│   │   ├── Hero.jsx               # Landing page hero section
│   │   ├── FeatureCards.jsx       # How InsightRAG works section
│   │   ├── AnimatedBackground.jsx # Particle animation background
│   │   ├── DocumentAnimation.jsx  # Lottie document animation
│   │   └── Footer.jsx
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx          # Main app — PDF library + chat
│   │   ├── Home.jsx               # Landing page
│   │   └── About.jsx              # About page
│   │
│   ├── services/
│   │   └── api.js                 # Axios calls to backend
│   │
│   └── App.jsx                    # Page routing and layout
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), Tailwind CSS, Axios, Framer Motion |
| Backend | FastAPI, Uvicorn, Python |
| Embeddings | BAAI/bge-small-en-v1.5 (SentenceTransformers) |
| Vector Store | FAISS (Flat L2 Index) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM | Groq — Llama-3.3-70b-versatile |
| PDF Parsing | PyMuPDF (fitz) |
| Image Captioning | BLIP (Salesforce/blip-image-captioning-base) |
| Table Extraction | Camelot |
| Excel Export | Pandas |

---

## RAG Pipeline

```
User Query
     ↓
Intent Detection (table / image / comparison / general)
     ↓
BGE Embedding Model
     ↓
FAISS Vector Search
     ↓
Balanced Retrieval across selected PDFs
     ↓
CrossEncoder Reranker
     ↓
Context Assembly (text + image captions)
     ↓
Groq LLM (Llama-3.3-70b)
     ↓
Answer + Excel (if table) + Images (if figure query)
```

---

## API Endpoints

### Upload PDF
```
POST /upload/
Content-Type: multipart/form-data
Body: file = <pdf file>
```

### Ask Question
```
POST /query/
Content-Type: application/json
Body:
{
  "question": "Your question here",
  "pdfs": ["document1.pdf", "document2.pdf"]
}
```

### Static Files
```
GET /images/{filename}           # Extracted PDF images
GET /generated_excels/{filename} # Auto-generated Excel files
```

---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/InsightRAG.git
cd InsightRAG
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run the server:
```bash
python run.py
```
Backend runs at `http://127.0.0.1:8000`

### 3. Frontend Setup
```bash
cd insightRAG-frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`

---

## Usage

1. Open the app and navigate to **Dashboard**
2. Upload one or more PDFs using the upload panel
3. Select the PDFs you want to query by checking them
4. Click **Initialize Chat** to start a session
5. Type your question in the chat input
6. Receive answers grounded in your document content
7. If the answer contains a table, an Excel file is auto-generated for download

---

## Future Enhancements

- Streaming LLM responses
- PDF viewer with highlighted source passages
- Persistent chat sessions across browser refreshes
- User authentication and session management
- Support for DOCX and TXT file formats
- Improved multimodal retrieval using vision-language models

---

## License

This project is open-source and available under the MIT License.

---

## Acknowledgements

- [Hugging Face](https://huggingface.co) — BGE embeddings, BLIP, CrossEncoder
- [Groq](https://groq.com) — Llama-3 inference
- [FAISS](https://github.com/facebookresearch/faiss) — Vector similarity search
- [PyMuPDF](https://pymupdf.readthedocs.io) — PDF parsing
- [Framer Motion](https://www.framer.com/motion/) — UI animations

---

> InsightRAG bridges the gap between static documents and interactive AI-driven knowledge systems.
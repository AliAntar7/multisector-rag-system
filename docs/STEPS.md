# Implementation Roadmap & System Steps

This document outlines the concise step-by-step implementation sequence and architecture for building the **Multisector RAG System**.

---

## 1. System Architecture & Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **API Backend** | FastAPI + Uvicorn | High-throughput asynchronous REST endpoints & static file serving |
| **Embedding Model** | Hugging Face (`all-MiniLM-L6-v2`) | Local 384-dimensional dense vector generation |
| **Vector Database** | Qdrant Cloud (Free Tier) | Similarity vector indexing, payload metadata, and sector filtering |
| **Document Store** | MongoDB Atlas (Free Tier) | Conversation history, chat sessions, and audit logging |
| **LLM Synthesis** | Groq / Gemini API | Generating grounded answers with source citations |
| **Client UI** | Vanilla HTML / CSS / JavaScript | Single-page interface for PDF ingestion & real-time chat |
| **Testing** | Postman Collection (.json) | Automated testing endpoints & manual verification |

---

## 2. Step-by-Step Implementation Sequence

### Step 1: Environment & Cloud Services Setup
* Initialize local Python virtual environment (`venv`).
* Install core dependencies (`fastapi`, `uvicorn`, `qdrant-client`, `pymongo`, `sentence-transformers`, `pypdf`, `reportlab`, `python-dotenv`).
* Configure cloud credentials in `.env`:
  * `QDRANT_URL` and `QDRANT_API_KEY` (Qdrant Cloud)
  * `MONGODB_URI` (MongoDB Atlas)
  * `LLM_API_KEY` (Groq / Gemini)

### Step 2: Dataset Generation (1,000 Structured Items)
* Create `scripts/generate_dataset.py` using `reportlab`.
* Generate a structured multi-page PDF containing 1,000 records partitioned across 3 sectors:
  * **E-Commerce Inventory** (~350 items: ID, Title, Category, Specs, Price)
  * **Healthcare Protocols** (~350 items: ID, Protocol Name, Condition, Guidelines, Precautions)
  * **Financial Assets** (~300 items: ID, Asset Class, Risk Level, Return Profile, Strategy)

### Step 3: PDF Ingestion & Text Chunking Engine
* Build document parsing utility using `pypdf` to read the sector-specific PDF.
* Segment text into structured context chunks (preserving `item_id`, `sector`, and `source_file` metadata).

### Step 4: Vector Embeddings & Qdrant Indexing
* Initialize Hugging Face `sentence-transformers/all-MiniLM-L6-v2`.
* Generate dense embeddings for each text chunk.
* Create a dedicated collection in Qdrant (e.g., `sector_knowledge_base`, cosine distance, 384 dimensions).
* Upsert vectors along with payload metadata (`sector`, `item_id`, `content`, `source_file`).

### Step 5: Retrieval & Conversational Pipeline (RAG + MongoDB)
* Convert incoming user query to vector via `all-MiniLM-L6-v2`.
* Perform similarity search in Qdrant with active sector payload filter (`filter={"sector": target_sector}`).
* Retrieve top $K$ relevant chunks and construct the augmented prompt.
* Query the LLM to synthesize an accurate answer with source citations.
* Persist session state, user query, response, and citations in MongoDB collection `chat_history`.

### Step 6: FastAPI Application Endpoints
* `POST /api/upload-pdf/`: Multipart form-data endpoint to upload, parse, vectorize, and index PDFs.
* `POST /api/chat/`: JSON payload endpoint receiving `{ query, sector, session_id }`, running RAG pipeline, and returning `{ answer, sources, session_id }`.
* `GET /`: Serve the static client interface.
* Verify auto-generated Swagger documentation at `/docs`.

### Step 7: Web Interface & Postman Export
* Develop clean, single-page web UI (`static/index.html` + CSS + JS):
  * Sector dropdown & file upload card with progress indicator.
  * Chat pane showing message bubbles, timestamps, and citation tags.
* Create and export Postman Collection (`multisector-rag-system.postman_collection.json`) with pre-configured request samples for upload and chat.

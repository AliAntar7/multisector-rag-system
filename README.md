# Multisector RAG System - DROSAT Educational Platform

An end-to-end **Retrieval-Augmented Generation (RAG)** chatbot architecture capable of ingesting large-scale multi-sector datasets (1,000 discrete structured items across curriculum courses, tutor schedules, and platform support policies), vectorizing content with Hugging Face transformers, persisting dense embeddings in **Qdrant Cloud**, maintaining conversational history in **MongoDB Atlas**, and serving queries through a high-throughput **FastAPI** backend with an interactive web UI.

---

## 🌟 Key Architecture & Tech Stack

| Layer | Component | Description |
| :--- | :--- | :--- |
| **REST API Backend** | **FastAPI + Uvicorn** | Asynchronous endpoint routing with auto-generated Swagger documentation (`/docs`) |
| **Embedding Model** | **Hugging Face (`all-MiniLM-L6-v2`)** | 384-dimensional dense semantic vectors running locally |
| **Vector Database** | **Qdrant Cloud** | High-performance similarity search with cosine distance and payload index filtering on `sector` |
| **Document Store** | **MongoDB Atlas** | NoSQL persistence for user session memory, interaction audit logs, and attribution sources |
| **Inference & LLM** | **Google Gemini Flash Lite** | Fast, strictly grounded generation with mandatory attribution citations |
| **Client Interface** | **Vanilla HTML5 / CSS3 / JavaScript** | Embedded single-page responsive dashboard supporting RTL Arabic and document ingestion |
| **Testing & Docs** | **Postman Collection & Pytest** | Structured `.json` collection export for contract testing |

---

## 🏗️ System Workflow & Pipelines

```text
1. [Data Ingestion Pipeline]:
   PDF Document (193 Pages, 1,000 Items)
       └──> Page-by-page Parsing & Chunking (app/services/pdf_parser.py)
               └──> Dense Vector Embeddings (all-MiniLM-L6-v2)
                       └──> Batch Upsert with Sector Metadata into Qdrant Cloud

2. [Conversational RAG Pipeline]:
   Student Question + Sector Tag + Session ID
       └──> Query Expansion & Translation (app/services/rag_service.py)
               └──> Cosine Similarity Search in Qdrant (Sector Filtered)
                       └──> Retrieve Top-K Context Chunks
                               └──> Fetch Session Context from MongoDB Atlas
                                       └──> Strict Grounding Prompt to Gemini Flash
                                               └──> Persist Turn to MongoDB Atlas
                                                       └──> Return Synthesized Response + Source Badges
```

---

## 📊 Sector Taxonomy (1,000 Discrete Items)

The system is pre-configured with a 1,000-item knowledge base for the **DROSAT Educational Platform**:

1. **`courses_curriculum` (400 Items: `CRS-0001` - `CRS-0400`):** Course codes, subjects (Physics, Chemistry, Math, Arabic, Biology), educational levels (1st, 2nd, 3rd Secondary / Thanaweya Amma), instructors, lesson counts, and pricing.
2. **`teachers_centers` (300 Items: `TCH-0001` - `TCH-0300`):** Tutor profiles, educational center locations (Nasr City, Maadi, Dokki, Mohandessin, Alexandria), weekly attendance shifts, hall capacities, and contact hotlines.
3. **`policies_support` (300 Items: `POL-0001` - `POL-0300`):** Platform regulations, Kashier payment gateway workflows, Fawry reference codes, booklet shipping terms (via Bosta Courier), and account security policies.

---

## 📁 Repository Structure

```text
multisector-rag-system/
├── app/
│   ├── config.py                 # Configuration & environment loader
│   ├── main.py                   # FastAPI application & endpoint routing
│   ├── schemas.py                # Pydantic request/response validation models
│   ├── services/
│   │   ├── chat_history.py       # MongoDB Atlas interaction & session management
│   │   ├── pdf_parser.py         # Multi-page PDF text extraction & chunking
│   │   ├── rag_service.py        # Core RAG orchestrator with Gemini synthesis
│   │   └── vector_store.py       # Qdrant Cloud client & embedding service
│   └── static/
│       ├── app.js                # Frontend client logic & API bindings
│       ├── index.html            # Single-page dashboard interface
│       └── style.css             # Responsive layout with Arabic RTL support
├── data/
│   ├── drosat_items.json         # Raw structured JSON export (1,000 items)
│   └── drosat_knowledge_base.pdf # 193-page master PDF catalog
├── docs/
│   ├── DECISIONS.md              # Architectural decisions & domain rationale
│   ├── PLAN.md                   # Phased execution checklist
│   ├── STEPS.md                  # Concise implementation guide
│   └── TASK.md                   # Original requirements specification
├── postman/
│   └── multisector_rag_system.postman_collection.json # Exported Postman collection
├── scripts/
│   ├── generate_drosat_dataset.py # Generates 1,000-item PDF catalog
│   ├── ingest_dataset.py         # Indexes 1,000 items into Qdrant Cloud
│   ├── test_api_endpoints.py     # Comprehensive REST API validation test
│   ├── test_connections.py       # Cloud services connectivity verification
│   └── test_rag.py               # End-to-end RAG conversational test
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git exclusions (protects .env and venv)
├── multisector-rag-system.postman_collection.json # Root Postman collection
├── requirements.txt              # Production dependencies
└── README.md                     # Project documentation
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
* Python 3.10+ (Tested on macOS / Linux / Windows)
* Free Qdrant Cloud cluster account ([cloud.qdrant.io](https://cloud.qdrant.io/))
* Free MongoDB Atlas M0 cluster ([mongodb.com/atlas](https://www.mongodb.com/atlas))
* Google Gemini API Key ([aistudio.google.com](https://aistudio.google.com/))

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/AliAntar7/multisector-rag-system.git
cd multisector-rag-system

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your cloud credentials:
```bash
cp .env.example .env
```
```ini
QDRANT_URL=https://<your-cluster-id>.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=<your_qdrant_api_key>

MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=drosat_rag_db

GEMINI_API_KEY=<your_gemini_api_key>
```

### 4. Verify Cloud Connections
Run the automated connectivity test to verify all cloud services:
```bash
python scripts/test_connections.py
```

### 5. Ingest 1,000 Items Dataset
To populate Qdrant Cloud with the 1,000 discrete structured items:
```bash
python scripts/ingest_dataset.py
```

### 6. Start the FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started, access:
* **Interactive Web Dashboard:** `http://localhost:8000/`
* **Swagger API Documentation:** `http://localhost:8000/docs`
* **ReDoc API Documentation:** `http://localhost:8000/redoc`

---

## 📡 REST API Reference

### 1. Chat & RAG
* **Endpoint:** `POST /api/chat/`
* **Request Body:**
```json
{
  "query": "محتاج تفاصيل كورس فيزياء تالتة ثانوي وسعره كام؟",
  "sector": "courses_curriculum",
  "session_id": "optional_session_uuid"
}
```
* **Response Sample:**
```json
{
  "session_id": "sess_da5ec450",
  "query": "محتاج تفاصيل كورس فيزياء تالتة ثانوي وسعره كام؟",
  "sector": "courses_curriculum",
  "answer": "أهلاً بك في منصة دروسات التعليمية! كورس الفيزياء المكثف للصف الثالث الثانوي متاح...",
  "sources": [
    {
      "item_id": "CRS-0199",
      "sector": "courses_curriculum",
      "source_file": "drosat_knowledge_base.pdf",
      "page": 35,
      "score": 0.6923
    }
  ]
}
```

### 2. Upload & Ingest PDF
* **Endpoint:** `POST /api/upload-pdf/`
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  * `file`: Binary PDF file.
  * `sector`: Target sector name (`courses_curriculum`, `teachers_centers`, `policies_support`, `general`).
* **Response Sample:**
```json
{
  "message": "PDF document successfully parsed and vectorized into Qdrant collection.",
  "filename": "custom_sector_document.pdf",
  "sector": "courses_curriculum",
  "chunks_extracted": 25,
  "vectors_indexed": 25,
  "status": "success"
}
```

### 3. System Health
* **Endpoint:** `GET /api/health`
* **Response:**
```json
{
  "status": "healthy",
  "application": "DROSAT Multisector RAG System",
  "version": "1.0.0",
  "qdrant_collection": "drosat_knowledge_base",
  "mongodb_database": "drosat_rag_db"
}
```

---

## 📮 Postman Collection

Import `multisector-rag-system.postman_collection.json` into Postman to run pre-configured test requests for:
1. `Check System Health`
2. `Get Web Dashboard Interface`
3. `Chat - Courses & Curriculum`
4. `Chat - Teachers & Centers`
5. `Chat - Policies & Payment Support`
6. `Chat - General / All Sectors`
7. `Chat - Out of Domain (Guardrail Check)`
8. `Upload Custom Sector PDF`

---

## 🛡️ Zero-Hallucination Guardrail

The system implements strict grounding rules in `app/services/rag_service.py`. When a query falls outside the indexed knowledge base (e.g., general world trivia):
* The similarity score threshold filters out unrelated chunks.
* The system prompt instructs the model to decline answering and guide the user back to DROSAT services.

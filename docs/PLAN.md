# Multisector RAG System - Project Execution Plan & Checklist

This document tracks the phased execution plan and checklist for building the end-to-end RAG system for the **DROSAT Educational Platform**.

---

## Progress Overview
* [x] **Phase 1: Infrastructure & Cloud Services Setup** (Completed)
* [x] **Phase 2: DROSAT Dataset Generation (1,000 Items PDF)** (Completed)
* [x] **Phase 3: Parsing, Chunking & Vector Ingestion (Qdrant)** (Completed)
* [x] **Phase 4: Core RAG Retrieval & Conversational Pipeline (MongoDB & LLM)** (Completed)
* [x] **Phase 5: FastAPI Backend REST Endpoints** (Completed)
* [ ] **Phase 6: Interactive Web Dashboard (Vanilla HTML/CSS/JS)**
* [ ] **Phase 7: Testing, Postman Collection & Deliverables**

---

## Detailed Phases & Sub-tasks

### Phase 1: Infrastructure & Cloud Services Setup
- [x] **1.1** Initialize Python Virtual Environment (`venv`) in project root.
- [x] **1.2** Create `requirements.txt` with all required dependencies (`fastapi`, `uvicorn`, `qdrant-client`, `pymongo`, `sentence-transformers`, `google-generativeai`, `pypdf`, `reportlab`, `python-dotenv`).
- [x] **1.3** Set up free **Qdrant Cloud** cluster and obtain `QDRANT_URL` and `QDRANT_API_KEY`.
- [x] **1.4** Set up free **MongoDB Atlas** M0 cluster and obtain `MONGODB_URI`.
- [x] **1.5** Set up **Google Gemini API** key (`GEMINI_API_KEY`).
- [x] **1.6** Configure environment variables in `.env` and `.env.example`.
- [x] **1.7** Create a verification connectivity script (`scripts/test_connections.py`) to validate access to Qdrant, MongoDB, and Gemini before writing application code.

### Phase 2: DROSAT Dataset Generation (1,000 Items PDF)
- [x] **2.1** Create dataset generation script (`scripts/generate_drosat_dataset.py`) using `reportlab`.
- [x] **2.2** Structure 1,000 distinct items distributed across 3 DROSAT sectors:
  - `courses_curriculum` (~400 items: Course ID, Subject, Grade Level, Teacher, Syllabus, Price)
  - `teachers_centers` (~300 items: Teacher ID, Name, Center Name, Location/Zone, Weekly Schedule, Contact)
  - `policies_support` (~300 items: Policy/FAQ ID, Topic, Rules, Payment/Kashier guides, Delivery terms)
- [x] **2.3** Compile and export the multi-page styled PDF to `data/drosat_knowledge_base.pdf`.
- [x] **2.4** Validate PDF structure, page numbers, and item count.

### Phase 3: Parsing, Chunking & Vector Ingestion (Qdrant)
- [x] **3.1** Build PDF parsing module (`app/services/pdf_parser.py`) to extract text and track page indices.
- [x] **3.2** Implement structured chunking preserving metadata: `sector`, `item_id`, `source_file`, and `content`.
- [x] **3.3** Initialize Hugging Face `sentence-transformers/all-MiniLM-L6-v2` locally for 384-dimensional dense vectors.
- [x] **3.4** Initialize Qdrant collection `drosat_knowledge_base` with Cosine distance and create payload indexes for `sector`.
- [x] **3.5** Build batch upsert ingestion script (`app/services/vector_store.py`) to index all 1,000 items into Qdrant.

### Phase 4: Core RAG Retrieval & Conversational Pipeline (MongoDB & LLM)
- [x] **4.1** Implement vector search query function with dynamic sector filtering (`filter={"sector": sector}`).
- [x] **4.2** Build strict RAG prompt template enforcing grounded answers and mandatory source citations (`[Source: DROSAT Catalog, Page X, Item ID]`).
- [x] **4.3** Connect Google Gemini Flash LLM to synthesize answers based on retrieved context.
- [x] **4.4** Implement MongoDB chat history service (`app/services/chat_history.py`) to persist `session_id`, queries, responses, sources, and timestamps.
- [x] **4.5** Create a CLI test script (`scripts/test_rag.py`) to test end-to-end chat queries and sector isolation.

### Phase 5: FastAPI Backend REST Endpoints
- [x] **5.1** Set up FastAPI application (`app/main.py`) with CORS middleware and structured routers.
- [x] **5.2** Define Pydantic request and response models (`app/schemas.py`).
- [x] **5.3** Implement `POST /api/upload-pdf/`: Uploads, parses, vectorizes, and indexes new PDFs into Qdrant.
- [x] **5.4** Implement `POST /api/chat/`: Accepts `{ query, sector, session_id }`, executes RAG, logs to MongoDB, and returns answer with attribution sources.
- [x] **5.5** Verify Swagger documentation at `/docs`.

### Phase 6: Interactive Web Dashboard (Vanilla HTML/CSS/JS)
- [ ] **6.1** Create static directory and serve `GET /` via FastAPI `StaticFiles`.
- [ ] **6.2** Design responsive single-page interface (`app/static/index.html`, `app/static/style.css`, `app/static/app.js`):
  - Document upload widget with active sector selector and upload progress.
  - Chat interface with real-time message stream, sector selector, source tags, and new session button.
- [ ] **6.3** Test cross-browser responsiveness and Arabic RTL rendering.

### Phase 7: Testing, Postman Collection & Deliverables
- [ ] **7.1** Export complete Postman Collection (`multisector-rag-system.postman_collection.json`) with pre-configured requests for upload and chat queries.
- [ ] **7.2** Perform full verification audit against all items in `docs/TASK.md`.
- [ ] **7.3** Create comprehensive project `README.md` with setup instructions, environment variable guide, and execution commands.

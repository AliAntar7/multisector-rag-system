# End-to-End Retrieval-Augmented Generation (RAG) Chatbot System

## 1. Project Overview
Design, build, and deploy an end-to-end Retrieval-Augmented Generation (RAG) chatbot system capable of ingesting a large-scale dataset (representing 1,000 distinct items extracted from sector-specific PDFs), vectorizing the content, storing embeddings and metadata, and serving queries via a robust REST API equipped with an interactive web dashboard and Postman documentation.

---

## 2. Technical Stack Requirements
* **Language:** Python
* **Embeddings & ML:** Hugging Face sentence-transformers (e.g., `all-MiniLM-L6-v2`)
* **Document Database & Chat History:** MongoDB (for storing session logs, metadata, and conversational context)
* **Vector Database:** Qdrant (for high-performance vector similarity search)
* **API Framework:** FastAPI (for asynchronous high-throughput endpoint routing)
* **Testing & Documentation:** Postman Collection (JSON export) & Swagger UI (`/docs`)
* **User Interface:** Vanilla HTML/CSS/JavaScript responsive frontend embedded directly within the application

---

## 3. Functional Requirements & Architecture

### A. Dataset & Ingestion Module
* **Data Source Generation:** Generate or accept a multi-page PDF dataset containing 1,000 discrete structured items across a user-selectable domain/sector (e.g., E-Commerce Inventory, Healthcare Protocols, Financial Assets).
* **PDF Parsing & Chunking:** Build a Python utility to parse documents page-by-page or item-by-item, segmenting text into manageable context windows for optimal retrieval.

### B. Vector Storage & Indexing (Qdrant)
* **Embedding Generation:** Pass chunked text through the Hugging Face transformer model to generate dense numerical vectors.
* **Vector Upsertion:** Store vectors in Qdrant along with payload metadata (`sector`, `source_file`, `item_id`, and content text) to enable filtered searching.

### C. Conversational & Metadata Backend (MongoDB)
* **Chat Session Management:** Track and persist user session history, queries, and generated responses in MongoDB.
* **Sector Isolation:** Ensure vector search queries can be filtered dynamically based on the selected target sector.

### D. REST API Endpoints (FastAPI)
* `POST /api/upload-pdf/`: Uploads, parses, vectorizes, and indexes custom sector PDFs into Qdrant.
* `POST /api/chat/`: Accepts a sector tag and a user query, performs vector similarity search filtered by sector, compiles context, stores logs in MongoDB, and returns synthesized answers with attribution sources.
* `GET /`: Serves the static web client interface.

### E. Client Interface & Deliverables
* **Interactive Web UI:** A single-page dashboard featuring:
  * A file upload widget with active sector selection for document ingestion.
  * A real-time chat interface displaying message histories, answers, and source citations.
* **Postman Collection:** A fully structured `.json` export containing pre-configured requests for file uploads and RAG query testing.

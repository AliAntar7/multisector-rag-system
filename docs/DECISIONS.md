# Architecture & Project Decisions Record (ADR)

This document tracks all key technical, architectural, and business domain decisions made for the **Multisector RAG System**.

---

## 1. Business Domain & Niche Selection

* **Selected Domain:** **DROSAT Educational Platform (منصة دروسات التعليمية)**.
* **Rationale:** Tailoring the project to an active, real-world educational ecosystem (the DROSAT student & teacher platform) makes the deliverables tangible, realistic, and directly valuable rather than using generic mock data.
* **Sector Taxonomy (1,000 Items Total):**
  1. `courses_curriculum` (~400 items): Subject courses (Physics, Chemistry, Arabic, Math, etc.), educational stages (Primary, Prep, Secondary / Thanaweya Amma), teacher names, syllabus outlines, lesson counts, and pricing.
  2. `teachers_centers` (~300 items): Registered tutors, partner educational centers, geographical zones (Nasr City, Maadi, Dokki, etc.), weekly class schedules, and contact protocols.
  3. `policies_support` (~300 items): Platform rules, student enrollment codes, payment mechanisms (Kashier, Fawry), material/booklet delivery terms, refund rules, and technical support FAQs.

---

## 2. Infrastructure & Hosting Strategy (Cloud vs. Local Docker)

* **Decision:** Rely on fully managed **Free Cloud Services** instead of local Docker containers.
* **Vector Database:** **Qdrant Cloud** (Managed Free Tier Cluster)
  * Eliminates local container overhead and memory consumption on macOS.
  * Provides low-latency HTTP/gRPC vector similarity queries, native payload filtering, and HTTPS API endpoints.
* **Document & Chat Database:** **MongoDB Atlas** (Managed M0 Free Cluster)
  * 512 MB permanent free tier.
  * Stores session identifiers, chat history, prompt audit logs, and attribution sources without local maintenance.
* **Inference / LLM:** Cloud LLM API (Groq LLaMA 3 / Google Gemini)
  * Keeps the application lightweight on the development machine.
  * Fast response times with zero GPU setup required locally.

---

## 3. Machine Learning & Embedding Choice

* **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (from Hugging Face).
* **Dimensionality:** 384 dimensions.
* **Execution:** Ran locally via Python. Extremely fast, low memory footprint (~80 MB model size), and tailored for semantic similarity search.

---

## 4. Backend & API Structure

* **Framework:** **FastAPI** with `uvicorn`.
* **Endpoints:**
  * `POST /api/upload-pdf/`: Handles multipart form data for uploading, parsing, chunking, and upserting sector PDFs to Qdrant.
  * `POST /api/chat/`: Accepts `{ query, sector, session_id }`, performs filtered vector search, constructs context, queries LLM, logs session in MongoDB, and returns `{ answer, sources, session_id }`.
  * `GET /`: Serves static web frontend directly from FastAPI.
  * `GET /docs`: Interactive Swagger OpenAPI documentation.

---

## 5. User Interface & Deliverables

* **Client UI:** Lightweight single-page application built with Vanilla HTML, CSS, and modern JavaScript embedded directly in the project (`static/`).
* **Verification & Testing:** Fully configured Postman Collection (`multisector-rag-system.postman_collection.json`) export for testing API contracts.

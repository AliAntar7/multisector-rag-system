import os
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import QDRANT_COLLECTION, MONGODB_DB_NAME
from app.schemas import ChatRequest, ChatResponse, PDFUploadResponse, HealthResponse
from app.services.rag_service import RAGService
from app.services.pdf_parser import PDFParserService
from app.services.vector_store import VectorStoreService

# Create FastAPI application
app = FastAPI(
    title="DROSAT Multisector RAG System API",
    description="End-to-end Retrieval-Augmented Generation chatbot system serving 1,000 sector-specific knowledge base items with Qdrant, MongoDB Atlas, and Google Gemini.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lazy/Singleton Services initialization
_rag_service: Optional[RAGService] = None
_vector_store: Optional[VectorStoreService] = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

def get_vector_store() -> VectorStoreService:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store

# -------------------------------------------------------------
# 1. Health Endpoint
# -------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse, tags=["System Health"])
def health_check():
    return HealthResponse(
        status="healthy",
        application="DROSAT Multisector RAG System",
        version="1.0.0",
        qdrant_collection=QDRANT_COLLECTION,
        mongodb_database=MONGODB_DB_NAME
    )

# -------------------------------------------------------------
# 2. Chat & RAG Endpoint
# -------------------------------------------------------------
@app.post("/api/chat/", response_model=ChatResponse, tags=["Conversational RAG"])
def chat_endpoint(request: ChatRequest):
    """
    Accepts a student query, target sector tag, and optional session ID.
    Performs sector-isolated vector similarity search, compiles context,
    logs conversation in MongoDB, and returns synthesized answer with attribution sources.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty."
        )

    rag = get_rag_service()
    result = rag.chat(
        query=request.query,
        sector=request.sector,
        session_id=request.session_id
    )
    return ChatResponse(**result)

# -------------------------------------------------------------
# 3. PDF Ingestion Endpoint
# -------------------------------------------------------------
@app.post("/api/upload-pdf/", response_model=PDFUploadResponse, tags=["Document Ingestion"])
async def upload_pdf_endpoint(
    file: UploadFile = File(..., description="Target PDF document to parse and vectorize"),
    sector: str = Form("general", description="Target sector tag (e.g., courses_curriculum, teachers_centers, policies_support)")
):
    """
    Uploads a sector-specific PDF, extracts text page-by-page,
    segments content into discrete chunks with metadata, and indexes dense vectors into Qdrant.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF (.pdf) documents are accepted."
        )

    saved_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Parse and chunk
        chunks = PDFParserService.parse_pdf(saved_path, default_sector=sector)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text or items could be extracted from the uploaded PDF."
            )

        # 2. Vectorize and upsert to Qdrant
        v_store = get_vector_store()
        total_upserted = v_store.upsert_chunks(chunks)

        return PDFUploadResponse(
            message=f"PDF document successfully parsed and vectorized into Qdrant collection.",
            filename=file.filename,
            sector=sector,
            chunks_extracted=len(chunks),
            vectors_indexed=total_upserted,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and index PDF: {str(e)}"
        )
    finally:
        file.file.close()

# -------------------------------------------------------------
# 4. Root / Client Interface Endpoint
# -------------------------------------------------------------
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

@app.get("/", tags=["Client Interface"])
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "message": "DROSAT Multisector RAG System API is running.",
        "documentation": "/docs",
        "chat_endpoint": "/api/chat/",
        "upload_endpoint": "/api/upload-pdf/"
    })

# Mount static folder if it exists
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

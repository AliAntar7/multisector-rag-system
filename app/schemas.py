from typing import List, Optional, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., description="Student or user natural language question", example="محتاج تفاصيل كورس فيزياء تالتة ثانوي وسعره كام؟")
    sector: Optional[str] = Field("all", description="Target sector to isolate search (courses_curriculum, teachers_centers, policies_support, all)", example="courses_curriculum")
    session_id: Optional[str] = Field(None, description="Unique conversation session identifier", example="sess_abc123")

class AttributionSource(BaseModel):
    item_id: Optional[str] = Field(None, description="Item identifier from catalog")
    sector: Optional[str] = Field(None, description="Associated sector")
    source_file: Optional[str] = Field(None, description="Name of the source PDF document")
    page: Optional[int] = Field(None, description="Catalog page number")
    score: Optional[float] = Field(None, description="Vector similarity cosine score")

class ChatResponse(BaseModel):
    session_id: str
    query: str
    sector: str
    answer: str
    sources: List[AttributionSource]

class PDFUploadResponse(BaseModel):
    message: str
    filename: str
    sector: str
    chunks_extracted: int
    vectors_indexed: int
    status: str

class HealthResponse(BaseModel):
    status: str
    application: str
    version: str
    qdrant_collection: str
    mongodb_database: str

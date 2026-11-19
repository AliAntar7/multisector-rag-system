import uuid
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIM,
)

class VectorStoreService:
    _instance = None
    _model = None

    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)
        self.collection_name = QDRANT_COLLECTION
        if VectorStoreService._model is None:
            print(f"🔄 Loading embedding model: {EMBEDDING_MODEL_NAME}...")
            VectorStoreService._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.model = VectorStoreService._model

    def ensure_collection(self):
        """Creates the Qdrant collection and payload index if not present."""
        existing_collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing_collections:
            print(f"📦 Creating Qdrant collection '{self.collection_name}' (dim={EMBEDDING_DIM}, distance=Cosine)...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            
            # Create payload index on sector for fast isolated queries
            print("⚡ Creating payload index on 'sector'...")
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="sector",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            print("✅ Collection and payload indexes ready.")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Encodes a list of text strings into 384-dimensional dense vectors."""
        embeddings = self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Encodes a single query string into a normalized vector."""
        embedding = self.model.encode(query, show_progress_bar=False, normalize_embeddings=True)
        return embedding.tolist()

    def upsert_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """Embeds and uploads chunks to Qdrant in batches."""
        self.ensure_collection()
        total_upserted = 0
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["content"] for c in batch]
            vectors = self.embed_texts(texts)

            points = []
            for chunk, vec in zip(batch, vectors):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk['source_file']}_{chunk['item_id']}_{chunk['page']}"))
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vec,
                        payload={
                            "item_id": chunk.get("item_id", ""),
                            "sector": chunk.get("sector", "general"),
                            "source_file": chunk.get("source_file", ""),
                            "page": chunk.get("page", 1),
                            "content": chunk.get("content", ""),
                        },
                    )
                )

            self.client.upsert(collection_name=self.collection_name, points=points)
            total_upserted += len(points)
            print(f"   Indexed {total_upserted}/{total_chunks} vectors in Qdrant...")

        return total_upserted

    def search(
        self,
        query: str,
        sector: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Executes vector similarity search with optional sector isolation filter.
        """
        query_vector = self.embed_query(query)

        query_filter = None
        if sector and sector != "all":
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="sector",
                        match=MatchValue(value=sector)
                    )
                ]
            )

        # Use query_points (modern qdrant-client API)
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=score_threshold
        )

        results = []
        for hit in search_result.points:
            results.append({
                "score": round(hit.score, 4),
                "item_id": hit.payload.get("item_id"),
                "sector": hit.payload.get("sector"),
                "source_file": hit.payload.get("source_file"),
                "page": hit.payload.get("page"),
                "content": hit.payload.get("content"),
            })

        return results

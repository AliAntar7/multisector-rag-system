import os
import sys
import time

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pdf_parser import PDFParserService
from app.services.vector_store import VectorStoreService

def main():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/drosat_knowledge_base.pdf"))
    
    print("=" * 65)
    print("🚀 Starting Dataset Ingestion Pipeline to Qdrant Cloud")
    print("=" * 65)
    print(f"📄 Target PDF: {pdf_path}")
    
    # 1. Parse & Chunk
    start_time = time.time()
    print("\n[1/3] Parsing PDF & Generating Structured Chunks...")
    chunks = PDFParserService.parse_pdf(pdf_path)
    print(f"✅ Extracted {len(chunks)} discrete chunks.")
    
    # 2. Vectorize & Index in Qdrant
    print("\n[2/3] Vectorizing Chunks & Upserting into Qdrant Cloud...")
    vector_store = VectorStoreService()
    total_indexed = vector_store.upsert_chunks(chunks, batch_size=100)
    print(f"✅ Successfully indexed {total_indexed} points into Qdrant Cloud!")
    print(f"⏱️ Ingestion took: {time.time() - start_time:.2f} seconds")
    
    # 3. Validation Test Query
    print("\n[3/3] Running Validation Semantic Search Queries...")
    
    # Test Query 1: Courses sector
    q1 = "Physics mechanics for Thanawya Amma"
    print(f"\n🔍 Query: '{q1}' | Sector: 'courses_curriculum'")
    results1 = vector_store.search(q1, sector="courses_curriculum", top_k=2)
    for r in results1:
        print(f"   ⭐ [Score: {r['score']}] Item: {r['item_id']} (Page {r['page']}) -> {r['content'][:120]}...")
        
    # Test Query 2: Teachers sector
    q2 = "Nasr City centers and Abbas El-Akkad schedules"
    print(f"\n🔍 Query: '{q2}' | Sector: 'teachers_centers'")
    results2 = vector_store.search(q2, sector="teachers_centers", top_k=2)
    for r in results2:
        print(f"   ⭐ [Score: {r['score']}] Item: {r['item_id']} (Page {r['page']}) -> {r['content'][:120]}...")
        
    # Test Query 3: Policies sector
    q3 = "Kashier payment and Fawry code expiration time"
    print(f"\n🔍 Query: '{q3}' | Sector: 'policies_support'")
    results3 = vector_store.search(q3, sector="policies_support", top_k=2)
    for r in results3:
        print(f"   ⭐ [Score: {r['score']}] Item: {r['item_id']} (Page {r['page']}) -> {r['content'][:120]}...")

    print("\n" + "=" * 65)
    print("🎉 Phase 3 Ingestion & Indexing Verification Complete!")
    print("=" * 65)

if __name__ == "__main__":
    main()

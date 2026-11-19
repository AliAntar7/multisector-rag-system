import os
import sys

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def main():
    print("=" * 65)
    print("🧪 Testing FastAPI REST Endpoints via TestClient")
    print("=" * 65)

    client = TestClient(app)

    # 1. Test Health Endpoint
    print("\n[1/5] Testing GET /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"✅ Status {res.status_code}: {res.json()}")

    # 2. Test Root Endpoint
    print("\n[2/5] Testing GET /...")
    res = client.get("/")
    assert res.status_code == 200
    print(f"✅ Status {res.status_code}: {res.json()}")

    # 3. Test Swagger Docs
    print("\n[3/5] Testing GET /docs (Swagger UI)...")
    res = client.get("/docs")
    assert res.status_code == 200
    assert "SwaggerUIBundle" in res.text or "swagger" in res.text.lower()
    print("✅ Status 200: Swagger UI HTML served successfully!")

    # 4. Test Chat Endpoint
    print("\n[4/5] Testing POST /api/chat/...")
    chat_payload = {
        "query": "ما هي صلاحية كود فوري ومواعيد الشحن للمحافظات؟",
        "sector": "policies_support",
        "session_id": "test_api_session_001"
    }
    res = client.post("/api/chat/", json=chat_payload)
    assert res.status_code == 200, f"Chat failed with status {res.status_code}: {res.text}"
    chat_data = res.json()
    print(f"✅ Status {res.status_code}:")
    print(f"   Session ID: {chat_data['session_id']}")
    print(f"   Answer Snippet: {chat_data['answer'][:150]}...")
    print(f"   Attribution Sources Count: {len(chat_data['sources'])}")
    for src in chat_data['sources'][:2]:
        print(f"     - [{src['item_id']}] Page {src['page']} (Score: {src['score']})")

    # 5. Test PDF Upload Endpoint (Generate a minimal test PDF and upload)
    print("\n[5/5] Testing POST /api/upload-pdf/...")
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    
    test_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/test_upload_doc.pdf"))
    doc = SimpleDocTemplate(test_pdf_path)
    styles = getSampleStyleSheet()
    doc.build([Paragraph("[CRS-9999] Advanced Robotics Course - Lead Instructor Dr. Antar. Enrollment Price: 500 EGP.", styles['Normal'])])
    
    with open(test_pdf_path, "rb") as f:
        res = client.post(
            "/api/upload-pdf/",
            files={"file": ("test_upload_doc.pdf", f, "application/pdf")},
            data={"sector": "courses_curriculum"}
        )
    assert res.status_code == 200, f"Upload failed: {res.text}"
    upload_data = res.json()
    print(f"✅ Status {res.status_code}: {upload_data}")

    print("\n" + "=" * 65)
    print("🎉 All 5 FastAPI REST Endpoints Verified Successfully!")
    print("=" * 65)

if __name__ == "__main__":
    main()

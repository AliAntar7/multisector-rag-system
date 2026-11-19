import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "drosat_rag_db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("🔍 Testing Multisector RAG System Cloud Connections")
print("=" * 60)

# 1. Test MongoDB Atlas
print("\n[1/3] Testing MongoDB Atlas Connection...")
try:
    from pymongo import MongoClient
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    print("✅ MongoDB Atlas: Connected successfully! Ping OK.")
    db = mongo_client[MONGODB_DB_NAME]
    print(f"   Using database: {MONGODB_DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB Atlas Failed: {e}")

# 2. Test Qdrant Cloud
print("\n[2/3] Testing Qdrant Cloud Connection...")
try:
    from qdrant_client import QdrantClient
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10)
    collections = qdrant.get_collections()
    print("✅ Qdrant Cloud: Connected successfully!")
    print(f"   Existing collections: {[c.name for c in collections.collections]}")
except Exception as e:
    print(f"❌ Qdrant Cloud Failed: {e}")

# 3. Test Google Gemini API
print("\n[3/3] Testing Google Gemini API...")
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.5-flash-lite")
    response = model.generate_content("Say 'Connected' in one word.")
    print("✅ Google Gemini API: Connected successfully!")
    print(f"   Model response: {response.text.strip()}")
except Exception as e:
    print(f"❌ Google Gemini API Failed: {e}")

print("\n" + "=" * 60)
print("✨ Test Complete!")
print("=" * 60)

import os
import sys
import uuid

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.rag_service import RAGService
from app.services.chat_history import ChatHistoryService

def main():
    print("=" * 70)
    print("🤖 End-to-End RAG Conversational Pipeline Test (Qdrant + Gemini + MongoDB)")
    print("=" * 70)

    rag = RAGService()
    history_service = ChatHistoryService()
    test_session = f"test_user_{uuid.uuid4().hex[:8]}"
    print(f"🔑 Test Session ID: {test_session}\n")

    test_queries = [
        {
            "title": "Test 1: Courses & Curriculum Query",
            "query": "محتاج تفاصيل كورس فيزياء لتالتة ثانوي، سعره كام ومين المدرس والمحتوى؟",
            "sector": "courses_curriculum"
        },
        {
            "title": "Test 2: Teachers & Centers Query",
            "query": "عايز اعرف مواعيد وسنتر مستر محمد عبدالمعبود في مدينة نصر ورقم التواصل؟",
            "sector": "teachers_centers"
        },
        {
            "title": "Test 3: Policies & Support Query",
            "query": "كود فوري بيفضل شغال قد إيه والشحن للمحافظات بياخد كام يوم؟",
            "sector": "policies_support"
        },
        {
            "title": "Test 4: Out-of-Domain Question (Zero-Hallucination Guardrail)",
            "query": "مين كسب كأس العالم لسنة 2022؟",
            "sector": "courses_curriculum"
        }
    ]

    for t in test_queries:
        print("-" * 70)
        print(f"🎯 {t['title']}")
        print(f"❓ Student Query: {t['query']}")
        print(f"🏷️ Sector Filter: {t['sector']}")
        
        result = rag.chat(
            query=t['query'],
            sector=t['sector'],
            session_id=test_session
        )

        print(f"\n💬 DROSAT Assistant Response:\n{result['answer']}")
        print("\n📚 Attribution Sources Cited:")
        for s in result['sources']:
            print(f"   • [{s['item_id']}] (Sector: {s['sector']} | Page: {s['page']} | Score: {s['score']})")
        print()

    # Verify MongoDB persistence
    print("=" * 70)
    print("🗄️ Verifying MongoDB Persistence...")
    session_summary = history_service.get_session_summary(test_session)
    recent_turns = history_service.get_recent_history(test_session, limit=10)
    
    print(f"✅ Total turns recorded in MongoDB for {test_session}: {session_summary['message_count']}")
    print(f"🕒 Last interaction timestamp: {session_summary['last_interaction']}")
    print(f"✅ Successfully retrieved {len(recent_turns)} conversation turns from MongoDB Atlas!")
    print("=" * 70)
    print("🎉 Phase 4 Core RAG Pipeline Verification Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()

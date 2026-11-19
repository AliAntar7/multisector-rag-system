import uuid
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.config import GEMINI_API_KEY
from app.services.vector_store import VectorStoreService
from app.services.chat_history import ChatHistoryService

class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.chat_history = ChatHistoryService()
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        # Using the verified working model from Phase 1
        self.model = genai.GenerativeModel("gemini-3.5-flash-lite")

    def _build_context_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        recent_history: List[Dict[str, Any]],
        sector: Optional[str]
    ) -> str:
        # 1. Format Retrieved Context Chunks
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            block = (
                f"--- [Document {idx}] ---\n"
                f"Item ID: {chunk.get('item_id', 'N/A')}\n"
                f"Sector: {chunk.get('sector', 'N/A')}\n"
                f"Source File: {chunk.get('source_file', 'Catalog')}\n"
                f"Catalog Page: {chunk.get('page', 'N/A')}\n"
                f"Details: {chunk.get('content', '')}\n"
            )
            context_blocks.append(block)
        
        context_text = "\n".join(context_blocks) if context_blocks else "No matching catalog documents found for this query."

        # 2. Format Recent History
        history_blocks = []
        for turn in recent_history:
            history_blocks.append(f"Student: {turn['user_query']}")
            history_blocks.append(f"Assistant: {turn['assistant_response']}")
        history_text = "\n".join(history_blocks) if history_blocks else "No prior messages in this session."

        # 3. Comprehensive Grounded System Prompt
        sector_display = sector.replace("_", " ").title() if sector and sector != "all" else "All Sectors"
        
        system_prompt = f"""You are the official AI Assistant for the DROSAT Educational Platform (منصة دروسات التعليمية).
Your mission is to provide accurate, helpful, and courteous answers to students and parents based STRICTLY on the official DROSAT knowledge base provided below.

Active Search Sector: {sector_display}

=== OFFICIAL DROSAT KNOWLEDGE BASE (RETRIEVED CONTEXT) ===
{context_text}
==========================================================

=== RECENT CONVERSATION HISTORY ===
{history_text}
===================================

=== INSTRUCTIONS & GROUNDING RULES ===
1. Respond primarily in clear, courteous Egyptian Arabic (unless the student explicitly asks in English, then respond in English).
2. Answer the student's question accurately using ONLY facts stated in the RETRIEVED CONTEXT above.
3. ATTRIBUTION CITATIONS: For every factual claim (courses, instructors, prices, center schedules, addresses, payment rules), cite the source explicitly using this format:
   [المصدر: كتالوج دروسات، كود: ITEM_ID، صفحة: PAGE]
4. ZERO HALLUCINATION: If the answer cannot be found in the provided context, state clearly and politely:
   "عذراً، هذه المعلومة غير متوفرة في الدليل الرسمي الحالي لمنصة دروسات. يرجى مراجعة الدعم الفني أو التأكد من القطاع المحدد."
5. Never invent course fees, instructor names, phone numbers, or dates that are not in the context.

Current Student Query: {query}

Provide your structured, helpful response now:"""
        return system_prompt

    def _prepare_search_query(self, query: str) -> str:
        """
        Translates/expands Arabic queries to English for all-MiniLM-L6-v2 vector matching.
        """
        if any(ord(char) > 127 for char in query):
            try:
                trans_prompt = (
                    f"Convert this educational user query into a concise English search phrase "
                    f"for finding matching items in a course and center catalog. Output ONLY the English phrase:\n"
                    f"Query: {query}\n"
                    f"English Phrase:"
                )
                res = self.model.generate_content(trans_prompt)
                translated = res.text.strip().replace('"', '')
                if translated:
                    return translated
            except Exception:
                pass
        return query

    def chat(
        self,
        query: str,
        sector: Optional[str] = None,
        session_id: Optional[str] = None,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Executes end-to-end RAG:
        1. Translates/expands search query if needed for the English embedding model.
        2. Retrieves relevant vectors from Qdrant with sector filter.
        3. Retrieves recent session history from MongoDB.
        4. Synthesizes response via Google Gemini.
        5. Logs transaction to MongoDB.
        6. Returns structured answer and source citations.
        """
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:12]}"

        # 1. Prepare search query for all-MiniLM-L6-v2
        search_query = self._prepare_search_query(query)

        # 2. Retrieve from Qdrant
        retrieved_chunks = self.vector_store.search(
            query=search_query,
            sector=sector,
            top_k=top_k,
            score_threshold=0.20
        )

        # 2. Get history from MongoDB
        recent_history = self.chat_history.get_recent_history(session_id, limit=3)

        # 3. Generate Answer with Gemini
        prompt = self._build_context_prompt(query, retrieved_chunks, recent_history, sector)
        
        try:
            response = self.model.generate_content(prompt)
            answer_text = response.text.strip()
        except Exception as e:
            # Fallback if API has temporary rate limit or outage
            print(f"⚠️ Gemini generation error: {e}")
            if retrieved_chunks:
                top = retrieved_chunks[0]
                answer_text = (
                    f"بناءً على وثائق منصة دروسات:\n\n"
                    f"{top['content']}\n\n"
                    f"[المصدر: {top['source_file']}، كود: {top['item_id']}، صفحة: {top['page']}]"
                )
            else:
                answer_text = "عذراً، لم نتمكن من الوصول للمعلومة المطلوبة حالياً. يرجى المحاولة لاحقاً."

        # 4. Prepare attribution sources
        sources = [
            {
                "item_id": c.get("item_id"),
                "sector": c.get("sector"),
                "source_file": c.get("source_file"),
                "page": c.get("page"),
                "score": c.get("score")
            }
            for c in retrieved_chunks
        ]

        # 5. Persist turn in MongoDB
        self.chat_history.log_interaction(
            session_id=session_id,
            user_query=query,
            assistant_response=answer_text,
            sector=sector,
            sources=sources
        )

        return {
            "session_id": session_id,
            "query": query,
            "sector": sector or "all",
            "answer": answer_text,
            "sources": sources
        }

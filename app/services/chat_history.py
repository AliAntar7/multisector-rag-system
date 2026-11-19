from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, DESCENDING
from app.config import MONGODB_URI, MONGODB_DB_NAME

class ChatHistoryService:
    _instance = None

    def __init__(self):
        self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        self.db = self.client[MONGODB_DB_NAME]
        self.collection = self.db["chat_messages"]
        
        # Create indexes for fast lookup by session_id and timestamp
        self.collection.create_index([("session_id", 1), ("created_at", DESCENDING)])

    def log_interaction(
        self,
        session_id: str,
        user_query: str,
        assistant_response: str,
        sector: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Saves a complete query-answer turn into MongoDB."""
        record = {
            "session_id": session_id,
            "sector": sector or "all",
            "user_query": user_query,
            "assistant_response": assistant_response,
            "sources": sources or [],
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(record)
        return str(result.inserted_id)

    def get_recent_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves recent conversation turns for context memory."""
        cursor = self.collection.find(
            {"session_id": session_id}
        ).sort("created_at", DESCENDING).limit(limit)

        history = list(cursor)
        history.reverse()  # Return in chronological order
        return history

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Returns message count and last interaction for a session."""
        count = self.collection.count_documents({"session_id": session_id})
        last_msg = self.collection.find_one(
            {"session_id": session_id},
            sort=[("created_at", DESCENDING)]
        )
        return {
            "session_id": session_id,
            "message_count": count,
            "last_interaction": last_msg["created_at"].isoformat() if last_msg else None
        }

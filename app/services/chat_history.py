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

    def list_all_sessions(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Returns distinct sessions with their title (first query) and timestamp."""
        pipeline = [
            {"$sort": {"created_at": 1}},
            {"$group": {
                "_id": "$session_id",
                "title": {"$first": "$user_query"},
                "sector": {"$last": "$sector"},
                "last_active": {"$last": "$created_at"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"last_active": -1}},
            {"$limit": limit}
        ]
        results = list(self.collection.aggregate(pipeline))
        sessions = []
        for r in results:
            sessions.append({
                "session_id": r["_id"],
                "title": (r.get("title") or "محادثة جديدة")[:45],
                "sector": r.get("sector", "all"),
                "last_active": r["last_active"].isoformat() if "last_active" in r and r["last_active"] else None,
                "message_count": r.get("count", 0)
            })
        return sessions

    def get_full_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Returns all messages in a session in chronological order."""
        cursor = self.collection.find({"session_id": session_id}).sort("created_at", 1)
        messages = []
        for doc in cursor:
            messages.append({
                "user_query": doc.get("user_query", ""),
                "assistant_response": doc.get("assistant_response", ""),
                "sector": doc.get("sector", "all"),
                "sources": doc.get("sources", []),
                "created_at": doc["created_at"].isoformat() if "created_at" in doc else None
            })
        return messages

    def delete_session(self, session_id: str) -> bool:
        """Deletes all messages for a session."""
        result = self.collection.delete_many({"session_id": session_id})
        return result.deleted_count > 0

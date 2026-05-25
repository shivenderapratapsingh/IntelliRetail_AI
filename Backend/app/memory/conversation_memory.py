from pymongo import MongoClient
from datetime import datetime

from app.models.state import AgentState

from app.core.config import (
    MONGODB_URI,
    MONGODB_DATABASE
)


#mongo db connection

client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]

conversation_collection = db["conversation_memory"]


#save conversation

def save_conversation(state: AgentState):

    try:

        document = {

            "user_query": state.user_query,

            "route": state.route,

            "final_answer": state.final_answer,

            "generated_sql": state.generated_sql,

            "prediction": state.prediction,

            "anomaly_status": state.anomaly_status,

            "success": state.success,

            "created_at": datetime.utcnow()
        }

        conversation_collection.insert_one(document)

        return {
            "success": True
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


#get recent conversation

def get_recent_conversations(limit: int = 5):

    try:

        conversations = list(

            conversation_collection
            .find()
            .sort("created_at", -1)
            .limit(limit)
        )

        for convo in conversations:

            convo["_id"] = str(convo["_id"])

        return {
            "success": True,
            "conversations": conversations
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
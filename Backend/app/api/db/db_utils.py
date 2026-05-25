from datetime import datetime

from app.models.state import AgentState

from client import db



chats_collection = db["chats"]
messages_collection = db["messages"]


#save conversation

def save_chat(chat_id: str, user_id: str):
    try:
        document = {
            "user_id": user_id,
            "chat_id":chat_id,
            "created_at": datetime.utcnow()
        }

        chats_collection.insert_one(document)

        return {
            "success": True
        }
    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
    

def save_message(chat_id: str, state: AgentState):

    try:

        document = {
            "chat_id": chat_id,

            "user_query": state.user_query,

            "route": state.route,

            "final_answer": state.final_answer,

            "generated_sql": state.generated_sql,

            "created_at": datetime.utcnow()
        }

        messages_collection.insert_one(document)

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
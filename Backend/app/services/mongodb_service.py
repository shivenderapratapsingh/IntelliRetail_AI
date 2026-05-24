from pymongo import MongoClient

from app.core.config import (
    MONGODB_URI,
    MONGODB_DATABASE
)


# =========================================================
# MONGODB CLIENT
# =========================================================

client = MongoClient(MONGODB_URI)


# =========================================================
# DATABASE
# =========================================================

db = client[MONGODB_DATABASE]


# =========================================================
# COLLECTION
# =========================================================

conversation_collection = db["conversation_memory"]
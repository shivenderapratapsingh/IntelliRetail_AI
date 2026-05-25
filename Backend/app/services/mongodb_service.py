from pymongo import MongoClient

from app.core.config import (
    MONGODB_URI,
    MONGODB_DATABASE
)


#Mongodb client

client = MongoClient(MONGODB_URI)


#databse

db = client[MONGODB_DATABASE]


#collection

conversation_collection = db["conversation_memory"]
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
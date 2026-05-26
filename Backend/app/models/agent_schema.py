from typing import Optional, List, Dict

from pydantic import BaseModel


class AgentRequest(BaseModel):

    query: str

    chat_history: Optional[List[Dict]] = []
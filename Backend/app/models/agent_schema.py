from pydantic import BaseModel


#Agent request
class AgentRequest(BaseModel):

    query: str


#Agent response

class AgentResponse(BaseModel):

    success: bool

    routes: list[str]

    answer: str
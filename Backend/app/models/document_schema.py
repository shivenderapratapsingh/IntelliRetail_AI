from pydantic import BaseModel


#document request

class DocumentRequest(BaseModel):

    query: str


#document response

class DocumentResponse(BaseModel):

    success: bool

    answer: str

    sources: list[str]
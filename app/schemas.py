from pydantic import BaseModel
from typing import List, Optional, Literal

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class QueryRequest(BaseModel):
    """Request model for receiving user queries."""
    query: str
    history: Optional[List[Message]] = []


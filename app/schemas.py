from pydantic import BaseModel

class QueryRequest(BaseModel):
    """Request model for receiving user queries."""
    query: str


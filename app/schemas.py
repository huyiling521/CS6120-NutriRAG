from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class ParsedQuery(BaseModel):
    goal: Optional[str] = None
    preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

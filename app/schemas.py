from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str


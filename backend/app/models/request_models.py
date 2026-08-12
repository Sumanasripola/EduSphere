from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str
    pdfs: List[str]
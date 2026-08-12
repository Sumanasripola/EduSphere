from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.auth.dependencies import get_current_user
from app.repositories.documents import user_owns_documents
from app.services.document_query import answer_question

router = APIRouter(prefix="/query", tags=["Query"])


class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None


@router.post("/")
def ask_question(req: QueryRequest, user=Depends(get_current_user)):
    if req.document_ids and not user_owns_documents(user["id"], req.document_ids):
        raise HTTPException(status_code=403, detail="One or more documents don't belong to you.")

    result = answer_question(req.question, user["id"], req.document_ids)

    return {
        "answer": result.get("answer"),
        "citations": result.get("citations", []),
        "excel": result.get("excel"),
    }

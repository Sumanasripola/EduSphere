from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from app.auth.dependencies import get_current_user
from app.repositories.chat import (
    create_session, list_sessions_for_user, session_belongs_to_user,
    list_messages_for_session, add_message, rename_session,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


class CreateSessionRequest(BaseModel):
    name: str = "New Chat"


class RenameSessionRequest(BaseModel):
    name: str


class AddMessageRequest(BaseModel):
    role: str  # "user" | "assistant"
    text: str
    citations: Optional[List[Any]] = None
    images: Optional[List[Any]] = None
    excel_path: Optional[str] = None


@router.post("/sessions")
def new_session(req: CreateSessionRequest, user=Depends(get_current_user)):
    return create_session(user["id"], req.name)


@router.get("/sessions")
def get_sessions(user=Depends(get_current_user)):
    return list_sessions_for_user(user["id"])


@router.patch("/sessions/{session_id}")
def rename(session_id: str, req: RenameSessionRequest, user=Depends(get_current_user)):
    if not session_belongs_to_user(session_id, user["id"]):
        raise HTTPException(status_code=403, detail="Not your chat session")
    rename_session(session_id, req.name)
    return {"id": session_id, "name": req.name}


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, user=Depends(get_current_user)):
    if not session_belongs_to_user(session_id, user["id"]):
        raise HTTPException(status_code=403, detail="Not your chat session")
    return list_messages_for_session(session_id)


@router.post("/sessions/{session_id}/messages")
def post_message(session_id: str, req: AddMessageRequest, user=Depends(get_current_user)):
    if not session_belongs_to_user(session_id, user["id"]):
        raise HTTPException(status_code=403, detail="Not your chat session")
    return add_message(
        session_id, req.role, req.text,
        citations=req.citations, images=req.images, excel_path=req.excel_path,
    )


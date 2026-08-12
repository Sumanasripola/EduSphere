from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.utils.file_utils import save_upload
from app.services.document_pipeline import process_document, detect_doc_type

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    try:
        detect_doc_type(file.filename)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Supported: PDF, DOCX, XLSX, CSV, PNG, JPG.",
        )

    file_path = save_upload(file)
    result = process_document(file_path, file.filename, user["id"])

    if result["status"] == "failed":
        raise HTTPException(
            status_code=422,
            detail=result.get("reason", "Could not process this file."),
        )

    return {
        "message": "File processed successfully",
        "document_id": result["document_id"],
        "chunks_indexed": result["chunks_indexed"],
    }

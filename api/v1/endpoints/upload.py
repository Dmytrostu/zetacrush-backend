from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db
from services.upload_service import process_upload
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", summary="Upload a book file for summarization", description="Upload a PDF, TXT, or DOC file and receive a summary in JSON format. Requires JWT token.")
def upload_file(file: UploadFile = File(...), token: str = "", db: Session = Depends(get_db)) -> dict:
    """
    Upload a book file (PDF, TXT, DOC) and receive a summary in JSON format.
    - **file**: The book file to upload
    - **token**: JWT access token
    Returns a summary including main characters, synopsis, and easter egg.
    """
    logger.info(f"Upload request received for file: {file.filename}")
    try:
        result = process_upload(db, file, token)
        logger.info(f"File processed: {file.filename}")
        return result
    except HTTPException as e:
        logger.error(f"Upload error for file {file.filename}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during file upload for file {file.filename}")
        raise HTTPException(status_code=500, detail="Internal server error")

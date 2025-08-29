from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db, get_current_user_id
from services.upload_service import process_upload
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", summary="Upload a book file for summarization", description="Upload a PDF, TXT, or DOC file and receive a summary in JSON format. Requires JWT token.")
def upload_file(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict:
    """
    Upload a book file (PDF, TXT, DOC) and receive a summary in JSON format.
    - **file**: The book file to upload
    
    Authentication required via Bearer token.
    Returns a summary including main characters, synopsis, and easter egg.
    """
    logger.info(f"Upload request received for file: {file.filename} from user ID: {user_id}")
    try:
        result = process_upload(db, file, user_id)
        logger.info(f"File processed: {file.filename} for user ID: {user_id}")
        return result
    except HTTPException as e:
        logger.error(f"Upload error for file {file.filename}, user ID {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during file upload for file {file.filename}, user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

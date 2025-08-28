from sqlalchemy.orm import Session
from crud.user_crud import get_user_by_username
from crud.subscription_crud import get_subscription_by_user
from fastapi import HTTPException
from datetime import datetime
import shutil
import os
import logging
from utils.auth import validate_token
from utils.subscription import validate_subscription

logger = logging.getLogger(__name__)

def process_upload(db: Session, file, token: str) -> dict:
    """
    Service to process file upload and return a summary.
    Args:
        db (Session): SQLAlchemy session.
        file (UploadFile): Uploaded file object.
        token (str): User's access token.
    Returns:
        dict: Summarized data from the uploaded file.
    """
    logger.info(f"Processing upload for file: {getattr(file, 'filename', 'unknown')}")
    username = validate_token(token)
    user = get_user_by_username(db, username)
    if not user:
        logger.error("Invalid user.")
        raise HTTPException(status_code=401, detail="Invalid user")
    validate_subscription(db, user.id)
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    summary = {
        "main_characters": ["Alice", "Bob"],
        "synopsis": "This is a dummy synopsis.",
        "easter_egg": "First appearance of Alice."
    }
    os.remove(file_path)
    logger.info(f"File processed and summary returned for file: {file.filename}")
    return summary

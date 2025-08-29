from sqlalchemy.orm import Session
from crud.user_crud import get_user_by_id, increment_upload_count
from crud.subscription_crud import get_subscription_by_user, check_subscription_status
from crud.book_crud import create_book
from fastapi import HTTPException, UploadFile
import shutil
import os
import logging
from utils.subscription import validate_subscription
import uuid
from datetime import datetime
import json
from utils.book_analyzer import analyze_book_text
import PyPDF2
import io
import tempfile
from typing import Optional, Tuple

# Import python-docx conditionally to avoid startup errors if not installed
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("python-docx not available. Word documents will not be processed correctly.")

logger = logging.getLogger(__name__)

def prepare_storage_location(file: UploadFile) -> Tuple[str, str, str]:
    """
    Prepare appropriate storage location based on environment.
    
    Args:
        file (UploadFile): The uploaded file
        
    Returns:
        Tuple[str, str, str]: (file_path, storage_type, book_id)
    """
    from core.config import UPLOAD_FOLDER, IS_SERVERLESS
    
    # Generate a unique identifier
    book_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = getattr(file, 'filename', 'unknown')
    safe_filename = f"{timestamp}_{book_id}_{original_filename}"
    
    if IS_SERVERLESS:
        # In serverless environment, use /tmp
        uploads_dir = "/tmp/uploads"
        storage_type = "temporary"
    else:
        # In regular environment, use configured uploads folder
        uploads_dir = UPLOAD_FOLDER
        storage_type = "local"
    
    # Ensure directory exists
    try:
        os.makedirs(uploads_dir, exist_ok=True)
    except OSError as e:
        logger.warning(f"Failed to create directory {uploads_dir}: {e}")
        # Fallback to /tmp if we can't create the directory
        uploads_dir = "/tmp/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        storage_type = "temporary"
    
    # Return the full path and storage type
    return os.path.join(uploads_dir, safe_filename), storage_type, book_id

def save_to_cloud_storage(local_path: str, file_name: str) -> Optional[str]:
    """
    Upload a file to cloud storage (to be implemented in the future).
    
    Args:
        local_path (str): Path to local file
        file_name (str): Original file name
        
    Returns:
        Optional[str]: Cloud storage URL if successful, None otherwise
    """
    # TODO: Implement cloud storage upload (S3, Azure Blob, etc)
    logger.warning("Cloud storage upload not implemented yet")
    return None

def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """
    Extract text from uploaded files of various formats.
    
    Args:
        file_path (str): Path to the file.
        file_extension (str): File extension to determine format.
        
    Returns:
        str: Extracted text content.
        
    Raises:
        ValueError: If file format is unsupported.
    """
    file_extension = file_extension.lower()
    
    # Text file
    if file_extension in ['txt', 'md', 'rtf']:
        # Try different encodings
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Try to detect encoding
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
    
    # PDF file
    elif file_extension == 'pdf':
        text = []
        with open(file_path, 'rb') as f:
            try:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
                return '\n'.join(text)
            except Exception as e:
                logger.error(f"Error extracting text from PDF: {str(e)}")
                raise ValueError(f"Could not extract text from PDF: {str(e)}")
    
    # DOCX file
    elif file_extension == 'docx':
        if not DOCX_AVAILABLE:
            raise ValueError("DOCX processing is not available. Please install python-docx package.")
        
        try:
            doc = docx.Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise ValueError(f"Could not extract text from DOCX: {str(e)}")
    
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def process_upload(db: Session, file: UploadFile, user_id: int) -> dict:
    """
    Service to process file upload and return a summary.
    
    Args:
        db (Session): SQLAlchemy session.
        file (UploadFile): Uploaded file object.
        user_id (int): User's ID from token.
        
    Returns:
        dict: Summarized data from the uploaded file.
        
    Raises:
        HTTPException: If user not found, subscription invalid, or upload limit reached.
    """
    logger.info(f"Processing upload for file: {getattr(file, 'filename', 'unknown')}")
    
    # Validate user
    user = get_user_by_id(db, user_id)
    if not user:
        logger.error(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate subscription and check upload limits
    validate_subscription(db, user_id)
    
    # Check if user has reached upload limit
    if user.upload_count >= user.max_uploads:
        logger.error(f"Upload limit reached for user ID: {user_id}, count: {user.upload_count}, max: {user.max_uploads}")
        raise HTTPException(status_code=403, detail="Upload limit reached. Please upgrade your subscription.")
    
    # Get original filename and extension
    original_filename = getattr(file, 'filename', 'unknown')
    file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
    
    # Prepare storage location with appropriate fallbacks for serverless environments
    file_path, storage_type, book_id = prepare_storage_location(file)
    logger.info(f"Storing file at {file_path} (storage type: {storage_type})")
    
    # Save file with error handling for read-only filesystems
    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            file_content = file.file.read()
            file_size = len(file_content)
            buffer.write(file_content)
        
        # Reset file position for further processing
        file.file.seek(0)
        
    except OSError as e:
        if "Read-only file system" in str(e):
            # Special handling for read-only filesystem errors (common in serverless)
            logger.warning(f"Read-only filesystem detected. Using temporary file: {e}")
            
            # Use tempfile module for temporary storage
            temp_handle, temp_path = tempfile.mkstemp(suffix=f"_{original_filename}")
            try:
                with os.fdopen(temp_handle, 'wb') as tmp:
                    file.file.seek(0)
                    file_content = file.file.read()
                    file_size = len(file_content)
                    tmp.write(file_content)
                
                file_path = temp_path
                storage_type = "temporary"
                file.file.seek(0)
            except Exception as temp_err:
                logger.error(f"Failed to write to temporary file: {temp_err}")
                raise HTTPException(status_code=500, 
                                   detail="Server storage error. Could not save uploaded file.")
        else:
            # Re-raise other errors
            logger.error(f"File saving error: {e}")
            raise HTTPException(status_code=500, 
                              detail=f"Could not save uploaded file: {str(e)}")
    
    # Increment upload count
    user = increment_upload_count(db, user_id)
    
    try:
        # Extract text from the file
        extracted_text = extract_text_from_file(file_path, file_extension)
        
        # Analyze the book text
        analysis_result = analyze_book_text(extracted_text)
        
        # Create a formatted response
        summary = {
            "id": book_id,
            "filename": original_filename,
            "uploadedAt": datetime.now().isoformat(),
            "fileSize": file_size,
            "fileType": file_extension,
            "characters": [char["name"] for char in analysis_result["main_characters_details"]],
            "synopsis": "\n\n".join(analysis_result["synopsis"]),
            "easterEgg": analysis_result["easter_egg"],
            # Include detailed data for frontend formatting
            "charactersDetails": analysis_result["main_characters_details"],
            "synopsisList": analysis_result["synopsis"],
            "upload_info": {
                "uploadCount": user.upload_count,
                "maxUploads": user.max_uploads,
                "remainingUploads": user.max_uploads - user.upload_count
            }
        }
        
        # Mark storage path as temporary for serverless environments
        stored_path = file_path
        if storage_type == "temporary":
            # In production, you'd want to implement persistent storage (S3, etc.)
            stored_path = f"TEMP:{file_path}"
        
        # Save the book data to the database
        book = create_book(
            db=db,
            user_id=user_id,
            book_id=book_id,
            filename=original_filename,
            file_path=stored_path,
            file_size=file_size,
            file_type=file_extension,
            characters=analysis_result["main_characters_details"],
            synopsis=analysis_result["synopsis"],
            easter_egg=analysis_result["easter_egg"]
        )
        
        logger.info(f"Successfully processed file: {original_filename} for user ID: {user_id}")
        return summary
        
    except Exception as e:
        logger.exception(f"Error processing file {original_filename}: {str(e)}")
        
        # Return a simplified response with error message
        return {
            "id": book_id,
            "filename": original_filename,
            "uploadedAt": datetime.now().isoformat(),
            "fileSize": file_size,
            "fileType": file_extension,
            "characters": [],
            "synopsis": "There was an error processing your file.",
            "easterEgg": "None found.",
            "error": f"Error processing file: {str(e)}",
            "upload_info": {
                "uploadCount": user.upload_count,
                "maxUploads": user.max_uploads,
                "remainingUploads": user.max_uploads - user.upload_count
            }
        }

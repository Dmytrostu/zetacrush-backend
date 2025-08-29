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

# Import python-docx conditionally to avoid startup errors if not installed
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("python-docx not available. Word documents will not be processed correctly.")

logger = logging.getLogger(__name__)

from typing import Optional, Tuple
import tempfile
from fastapi import UploadFile

def prepare_storage_location(file: UploadFile) -> Tuple[str, str]:
    """
    Prepare appropriate storage location based on environment.
    
    Args:
        file (UploadFile): The uploaded file
        
    Returns:
        Tuple[str, str]: (file_path, storage_type) where storage_type is 'local' or 'temporary'
    """
    from core.config import UPLOAD_FOLDER, IS_SERVERLESS, IS_VERCEL
    
    # Generate a unique filename
    book_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = getattr(file, 'filename', 'unknown')
    safe_filename = f"{timestamp}_{book_id}_{original_filename}"
    
    if IS_SERVERLESS:
        # In serverless environment (Vercel), use /tmp which is the only writable location
        uploads_dir = "/tmp/uploads"
        storage_type = "temporary"
        logger.info(f"Using temporary storage directory: {uploads_dir} (Vercel environment detected: {IS_VERCEL})")
    else:
        # In regular environment, use configured uploads folder
        uploads_dir = UPLOAD_FOLDER
        storage_type = "local"
        logger.info(f"Using local storage directory: {uploads_dir}")
    
    # Ensure directory exists
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Return the full path and storage type
    return os.path.join(uploads_dir, safe_filename), storage_type

def save_to_cloud_storage(local_path: str, file_name: str) -> Optional[str]:
    """
    Upload a file to Google Drive.
    
    Args:
        local_path (str): Path to local file
        file_name (str): Original file name
        
    Returns:
        Optional[str]: Google Drive file ID if successful, None otherwise
    """
    from core.config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_CREDENTIALS_FILE, USE_CLOUD_STORAGE
    import os
    
    if not USE_CLOUD_STORAGE:
        logger.warning("Cloud storage is disabled. Set USE_CLOUD_STORAGE=true to enable.")
        return None
        
    if not GOOGLE_DRIVE_FOLDER_ID or not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        logger.error(f"Google Drive configuration missing: GOOGLE_DRIVE_FOLDER_ID={GOOGLE_DRIVE_FOLDER_ID}, GOOGLE_CREDENTIALS_FILE exists: {os.path.exists(GOOGLE_CREDENTIALS_FILE)}")
        return None
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2 import service_account
        
        # Generate a safe file name
        safe_file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}_{file_name}"
        
        # Set up credentials
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
            
        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Create file metadata
        file_metadata = {
            'name': safe_file_name,
            'parents': [GOOGLE_DRIVE_FOLDER_ID]
        }
        
        # Upload file
        media = MediaFileUpload(
            local_path,
            resumable=True
        )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink', '')
        
        logger.info(f"File uploaded to Google Drive with ID: {file_id}")
        
        # Return the file ID and web link
        return f"gdrive:{file_id}:{web_link}"
    
    except Exception as e:
        logger.exception(f"Error uploading to Google Drive: {str(e)}")
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
    
    # Create unique identifier for the book
    book_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = getattr(file, 'filename', 'unknown')
    safe_filename = f"{timestamp}_{book_id}_{original_filename}"
    
    # Get storage location using our helper function
    file_path, storage_type = prepare_storage_location(file)
    file_size = 0
    
    with open(file_path, "wb") as buffer:
        # Get file size while copying
        file_content = file.file.read()
        file_size = len(file_content)
        buffer.write(file_content)
    
    # Reset file position for potential future reads
    file.file.seek(0)
    
    # Increment upload count
    user = increment_upload_count(db, user_id)
    
    # Get file extension to determine processing method
    file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
    
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
        
        # In serverless environments, we can't rely on the local filesystem for persistent storage
        from core.config import IS_SERVERLESS, IS_VERCEL
        
        # If in serverless environment, we're using a temporary path
        stored_path = file_path
        if IS_SERVERLESS:
            # For Vercel, we'll just use the /tmp path but mark it as temporary
            if IS_VERCEL:
                stored_path = f"VERCEL_TMP:{file_path}"
                logger.info(f"Using Vercel temporary storage: {stored_path}")
            # For other environments, try cloud storage if enabled
            elif USE_CLOUD_STORAGE:
                cloud_path = save_to_cloud_storage(file_path, original_filename)
                if cloud_path:
                    stored_path = cloud_path
                    logger.info(f"File uploaded to cloud storage: {cloud_path}")
                else:
                    # If cloud upload fails, mark it as temporary
                    stored_path = f"TEMP:{file_path}"
                    logger.warning("Cloud storage upload failed, using temporary storage")
            else:
                # Just store a note that this is temporary storage
                stored_path = f"TEMP:{file_path}"
                logger.info("Using temporary storage (cloud storage disabled)")
            
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
        print(book)
        
        logger.info(f"Successfully processed file: {original_filename} for user ID: {user_id}")
        return summary
        
    except Exception as e:
        logger.exception(f"Error processing file {original_filename}: {str(e)}")
        # Even if processing fails, we've already incremented the upload count
        # In a production system, we might want to roll back the counter if processing fails
        
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

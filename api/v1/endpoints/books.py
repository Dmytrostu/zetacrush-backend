from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from core.dependencies import get_db, get_current_user_id
from schemas.book import BookHistoryResponse, BookHistoryItem
from crud.book_crud import get_user_books, delete_book, get_book_by_id

router = APIRouter()

@router.get("/history", response_model=BookHistoryResponse)
def get_book_history(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Retrieve the user's book upload history with pagination.
    
    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        BookHistoryResponse: Paginated list of book summaries.
    """
    result = get_user_books(db, user_id, skip, limit)
    
    # Transform database records into the expected format
    books = []
    for book in result["books"]:
        try:
            characters = json.loads(book.characters) if book.characters else []
            synopsis = json.loads(book.synopsis) if book.synopsis else []
            
            # Format the book data according to the schema
            books.append(BookHistoryItem(
                id=book.book_id,
                filename=book.filename,
                date=book.uploaded_at.isoformat(),
                summary={
                    "characters": [char["name"] for char in characters],
                    "synopsis": "\n\n".join(synopsis) if synopsis else "",
                    "easterEgg": book.easter_egg or ""
                }
            ))
        except Exception as e:
            # Skip problematic entries but log the error
            continue
    
    return BookHistoryResponse(
        books=books,
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"]
    )

@router.get("/{book_id}", summary="Get book details", description="Get detailed information about a specific book.")
def get_book_details(
    book_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get detailed information about a specific book.
    
    Args:
        book_id (str): Unique identifier for the book.
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        dict: Book details.
    """
    book = get_book_by_id(db, book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this book")
    
    try:
        characters = json.loads(book.characters) if book.characters else []
        synopsis = json.loads(book.synopsis) if book.synopsis else []
        
        return {
            "id": book.book_id,
            "filename": book.filename,
            "uploadedAt": book.uploaded_at.isoformat(),
            "fileSize": book.file_size,
            "fileType": book.file_type,
            "characters": [char["name"] for char in characters],
            "charactersDetails": characters,
            "synopsis": "\n\n".join(synopsis) if synopsis else "",
            "synopsisList": synopsis,
            "easterEgg": book.easter_egg or ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing book data: {str(e)}")

@router.get("/{book_id}/summary", summary="Get book summary", description="Get the summary for a specific book.")
def get_book_summary(
    book_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get the summary for a specific book.
    
    Args:
        book_id (str): Unique identifier for the book.
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        dict: Book summary with characters, synopsis, and easter egg.
    """
    book = get_book_by_id(db, book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this book")
    
    try:
        characters = json.loads(book.characters) if book.characters else []
        synopsis = json.loads(book.synopsis) if book.synopsis else []
        
        return {
            "id": book.book_id,
            "filename": book.filename,
            "characters": [char["name"] for char in characters],
            "synopsis": "\n\n".join(synopsis) if synopsis else "",
            "easterEgg": book.easter_egg or ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing book summary: {str(e)}")

@router.delete("/{book_id}")
def delete_book_endpoint(
    book_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a book from the user's history.
    
    Args:
        book_id (str): Unique identifier for the book.
        db (Session): Database session.
        user_id (int): Current user ID.
        
    Returns:
        dict: Success message.
    """
    deleted = delete_book(db, book_id, user_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found or not owned by the user")
    
    return {"message": "Book deleted successfully"}

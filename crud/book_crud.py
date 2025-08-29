from sqlalchemy.orm import Session
from models.book import Book
from models.user import User
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from sqlalchemy import desc

def create_book(
    db: Session,
    user_id: int,
    book_id: str,
    filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
    characters: List[Dict[str, Any]],
    synopsis: List[str],
    easter_egg: str
) -> Book:
    """
    Create a new book entry in the database.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
        book_id (str): Unique identifier for the book.
        filename (str): Original filename.
        file_path (str): Path to the stored file.
        file_size (int): Size of the file in bytes.
        file_type (str): Type of the file.
        characters (List[Dict[str, Any]]): List of character dictionaries.
        synopsis (List[str]): List of synopsis passages.
        easter_egg (str): Easter egg passage.
        
    Returns:
        Book: Created book ORM object.
    """
    # Convert Python objects to JSON strings for storage
    characters_json = json.dumps(characters)
    synopsis_json = json.dumps(synopsis)
    
    # Create new book
    book = Book(
        user_id=user_id,
        book_id=book_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        characters=characters_json,
        synopsis=synopsis_json,
        easter_egg=easter_egg
    )
    
    db.add(book)
    db.commit()
    db.refresh(book)
    
    return book

def get_book_by_id(db: Session, book_id: str) -> Optional[Book]:
    """
    Get a book by its book_id.
    
    Args:
        db (Session): SQLAlchemy session.
        book_id (str): Unique identifier for the book.
        
    Returns:
        Book or None: Book ORM object if found, else None.
    """
    return db.query(Book).filter(Book.book_id == book_id).first()

def get_user_books(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get all books for a specific user with pagination.
    
    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User's ID.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        
    Returns:
        Dict[str, Any]: Dictionary with books and pagination info.
    """
    # Get total count
    total = db.query(Book).filter(Book.user_id == user_id).count()
    
    # Get paginated books sorted by upload date (newest first)
    books = db.query(Book).filter(Book.user_id == user_id)\
             .order_by(desc(Book.uploaded_at))\
             .offset(skip).limit(limit).all()
    
    return {
        "books": books,
        "total": total,
        "limit": limit,
        "offset": skip
    }

def delete_book(db: Session, book_id: str, user_id: int) -> bool:
    """
    Delete a book by its book_id if it belongs to the specified user.
    
    Args:
        db (Session): SQLAlchemy session.
        book_id (str): Unique identifier for the book.
        user_id (int): User's ID for verification.
        
    Returns:
        bool: True if deleted, False if not found or not owned by the user.
    """
    book = db.query(Book).filter(
        Book.book_id == book_id,
        Book.user_id == user_id
    ).first()
    
    if book:
        db.delete(book)
        db.commit()
        return True
    return False

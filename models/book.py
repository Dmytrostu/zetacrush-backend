from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Book(Base):
    """
    SQLAlchemy ORM model for the Book table.
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to User.
        book_id (str): Unique identifier for the book (UUID).
        filename (str): Original filename.
        file_path (str): Path to the stored file.
        file_size (int): Size of the file in bytes.
        file_type (str): Type of the file (e.g. pdf, txt).
        uploaded_at (datetime): When the book was uploaded.
        characters (str): JSON string of main characters.
        synopsis (str): JSON string of synopsis passages.
        easter_egg (str): Easter egg passage.
        user (User): Relationship to User.
    """
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    characters = Column(Text)  # Stored as JSON
    synopsis = Column(Text)  # Stored as JSON
    easter_egg = Column(Text)
    
    user = relationship("User", backref="books")

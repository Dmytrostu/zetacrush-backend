from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class BookCharacter(BaseModel):
    name: str
    occurrences: int

class BookSummaryBase(BaseModel):
    id: str
    filename: str
    uploadedAt: str
    fileSize: Optional[int] = None
    fileType: Optional[str] = None
    characters: List[str]
    synopsis: str
    easterEgg: str
    
class BookSummaryCreate(BookSummaryBase):
    characters_details: List[BookCharacter]
    synopsis_list: List[str]
    
class BookSummaryInDB(BookSummaryBase):
    user_id: int
    file_path: str
    
    class Config:
        from_attributes = True

class BookHistoryItem(BaseModel):
    id: str
    filename: str
    date: str
    summary: Dict[str, Any]
    
class BookHistoryResponse(BaseModel):
    books: List[BookHistoryItem]
    total: int
    limit: int
    offset: int

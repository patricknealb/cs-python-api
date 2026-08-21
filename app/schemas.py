from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageCreate(BaseModel):
    message_id: Optional[str] = None
    message_text: str
    message_category_id: int

class MessageUpdate(BaseModel):
    message_text: Optional[str] = None
    message_category_id: Optional[int] = None

class MessageResponse(BaseModel):
    row_id: int
    message_id: str
    message_text: str
    message_category_id: int
    published: bool
    row_created_at: datetime
    row_updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
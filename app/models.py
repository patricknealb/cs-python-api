from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, func
from app.database import Base

class Message(Base):
    __tablename__ = "message"
    __table_args__ = {"schema": "cs_data"}

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(64), nullable=False, unique=True)
    message_text = Column(String, nullable=False)
    message_category_id = Column(Integer, nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    external = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    favourite_count = Column(Integer, nullable=False, default=0)
    row_created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    row_updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
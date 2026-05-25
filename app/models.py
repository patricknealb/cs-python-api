from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from app.database import Base

class Message(Base):
    __tablename__ = "message"
    __table_args__ = {"schema": "cs_data"}

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(64), nullable=False, unique=True)
    message_text = Column(String, nullable=False)
    message_category_id = Column(Integer, ForeignKey("cs_data.message_category.message_category_id"), nullable=False)
    row_created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    row_updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
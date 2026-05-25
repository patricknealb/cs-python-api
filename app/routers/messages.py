from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.database import get_db
from app.models import Message
from app.schemas import MessageCreate, MessageUpdate, MessageResponse
from app.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  #disable to test without security
):
    """Insert a new message. Returns 409 if message_id already exists."""
    message = Message(**payload.model_dump())
    db.add(message)
    try:
        await db.commit()
        await db.refresh(message)
        return message
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Message with message_id '{payload.message_id}' already exists"
        )


@router.put("/{message_id}", response_model=MessageResponse)
async def upsert_message(
    message_id: str,
    payload: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Update existing message, or insert if it doesn't exist (upsert)."""
    result = await db.execute(
        select(Message).where(Message.message_id == message_id)
    )
    message = result.scalar_one_or_none()

    if message:
        # Update existing
        update_data = payload.model_dump(exclude_unset=True)
        update_data["row_updated_at"] = datetime.now(timezone.utc)
        for key, value in update_data.items():
            setattr(message, key, value)
    else:
        # Insert new
        if not payload.message_text or not payload.message_category_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="message_text and message_category_id are required for new messages"
            )
        message = Message(
            message_id=message_id,
            **payload.model_dump(exclude_unset=True)
        )
        db.add(message)

    await db.commit()
    await db.refresh(message)
    return message


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  #disable to test without security
):
    """Get a message by message_id."""
    result = await db.execute(
        select(Message).where(Message.message_id == message_id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message '{message_id}' not found"
        )
    return message


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  #disable to test without security
):
    """Get all messages with pagination."""
    result = await db.execute(
        select(Message).offset(skip).limit(limit)
    )
    return result.scalars().all()
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import uuid
import resend

from app.database import get_db
from app.models import Message, MessageCategory
from app.config import settings

router = APIRouter(tags=["submit"])

resend.api_key = settings.resend_api_key


class MessageSubmission(BaseModel):
    message_text: str
    email: str


@router.post("/submit")
async def submit_message(
    payload: MessageSubmission,
    db: AsyncSession = Depends(get_db)
):
    # Generate a unique token for email verification
    token = str(uuid.uuid4())
    message_id = str(uuid.uuid4())

    # Save message as unpublished with token stored in message_id prefix
    # We store token in a separate field by reusing message_id format: token|message_id
    message = Message(
        message_id=f"{token}|{message_id}",
        message_text=payload.message_text,
        message_category_id=1,  # default category
        published=False
    )
    db.add(message)
    await db.commit()

    # Send verification email
    verify_url = f"{settings.verify_base_url}/verify/{token}"

    resend.Emails.send({
        "from": "Common Sense <onboarding@resend.dev>",
        "to": payload.email,
        "subject": "Verify your Common Sense message submission",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #2c3e50; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: #e67e22; margin: 0; font-size: 32px;">CS</h1>
                <p style="color: #ffffff; margin: 8px 0 0 0;">Common Sense</p>
            </div>
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                <p style="color: #2c3e50; font-size: 16px;">Thanks for submitting a Common Sense message!</p>
                <p style="color: #2c3e50; font-size: 16px;">Click the link below to verify your email. Your message will be reviewed before publishing.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}"
                       style="background: #e67e22; color: white; padding: 14px 32px; border-radius: 6px;
                              text-decoration: none; font-weight: bold; font-size: 16px;">
                        Verify My Submission
                    </a>
                </div>
                <p style="color: #7f8c8d; font-size: 13px;">
                    Your message: <em>"{payload.message_text[:100]}{'...' if len(payload.message_text) > 100 else ''}"</em>
                </p>
                <p style="color: #7f8c8d; font-size: 12px;">If you didn't submit a message, you can ignore this email.</p>
            </div>
        </div>
        """
    })

    return {"message": "Submission received. Please check your email to verify."}


@router.get("/verify/{token}", response_class=HTMLResponse)
async def verify_message(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    # Find message with this token
    result = await db.execute(
        select(Message).where(Message.message_id.like(f"{token}|%"))
    )
    message = result.scalar_one_or_none()

    if not message:
        return HTMLResponse(content="""
            <html>
            <body style="font-family:Arial; text-align:center; padding:60px; background:#2c3e50; color:white;">
                <h1 style="color:#e67e22;">CS</h1>
                <h2>Invalid or expired link</h2>
                <p>This verification link is invalid or has already been used.</p>
            </body>
            </html>
        """, status_code=404)

    # Clean up the message_id to remove the token prefix
    message.message_id = message.message_id.split("|")[1]
    message.row_updated_at = datetime.now(timezone.utc)
    await db.commit()

    return HTMLResponse(content="""
        <html>
        <body style="font-family:Arial; text-align:center; padding:60px; background:#2c3e50; color:white;">
            <h1 style="color:#e67e22;">CS</h1>
            <h2 style="color:#ffffff;">Thank you!</h2>
            <p style="color:#bdc3c7;">Your message has been verified and is now pending review.</p>
            <p style="color:#bdc3c7;">We'll publish it once it's been approved.</p>
            <a href="/" style="color:#e67e22;">← Back to Common Sense</a>
        </body>
        </html>
    """)
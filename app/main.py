from fastapi import FastAPI
from app.routers import messages

app = FastAPI(title="Common Sense API")

app.include_router(messages.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
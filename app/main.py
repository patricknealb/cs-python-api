from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import messages

app = FastAPI(title="CS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cs-website-b39g.onrender.com",  # your exact Render URL
        "http://localhost:3000",  # for local testing
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
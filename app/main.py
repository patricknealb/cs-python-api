from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import messages, submit

app = FastAPI(title="CS API")

# Allow requests from the website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your domain once live
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages.router)
app.include_router(submit.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
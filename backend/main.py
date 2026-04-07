"""Main FastAPI application"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, analyze, stickers, emotions

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Sticker AI Backend",
    description="API for AI-powered sticker generation",
    version="1.0.0"
)

# Configure CORS
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
_allowed_origins = ["*"] if _raw_origins.strip() == "*" else [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(stickers.router)
app.include_router(emotions.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sticker AI Backend",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

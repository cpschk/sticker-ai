"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, analyze, stickers, emotions


# Create FastAPI app
app = FastAPI(
    title="Sticker AI Backend",
    description="API for AI-powered sticker generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

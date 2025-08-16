from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.features.ai_analysis.controllers.ai_controller import router as ai_router

app = FastAPI(
    title="RepoLens API",
    description="AI-powered codebase analysis and visualization API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TODO:update later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include feature routers
app.include_router(ai_router)

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "RepoLens API is live",
        "version": "1.0.0",
        "features": ["ai_analysis"]
    }

@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "RepoLens API",
        "version": "1.0.0"
    }

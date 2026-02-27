from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import settings
from backend.database import engine
from backend.models import Base, Notebook, Document, Conversation, Message
from backend.config_model import Config
from backend.routers import notebooks, documents, chat, content, config, podcast
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="NotebookLM API",
    description="AI-powered intelligent notebook assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(
    notebooks.router,
    prefix=f"{settings.API_V1_PREFIX}/notebooks",
    tags=["notebooks"]
)

app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_PREFIX}/documents",
    tags=["documents"]
)

app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_PREFIX}/chat",
    tags=["chat"]
)

app.include_router(
    content.router,
    prefix=f"{settings.API_V1_PREFIX}/content",
    tags=["content"]
)

app.include_router(
    config.router,
    prefix=f"{settings.API_V1_PREFIX}/config",
    tags=["config"]
)

app.include_router(
    podcast.router,
    prefix=f"{settings.API_V1_PREFIX}/podcast",
    tags=["podcast"]
)

# Mount static files for frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

@app.get("/")
def root():
    if os.path.exists(os.path.join(static_dir, "index.html")):
        return FileResponse(os.path.join(static_dir, "index.html"))
    return {
        "message": "NotebookLM API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.head("/")
def root_head():
    return ""

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# SPA fallback - serve index.html for all non-API routes

@app.get("/{path:path}")
async def spa_fallback(path: str):
    # Skip API routes, docs, and health check
    if path.startswith("api") or path.startswith("docs") or path.startswith("health"):
        # Let API routes be handled by their respective routers
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if it's a static file
    file_path = os.path.join(static_dir, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Serve index.html for SPA routing
    if os.path.exists(os.path.join(static_dir, "index.html")):
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    return {"message": "Frontend not built. Run 'cd frontend && pnpm build' first."}

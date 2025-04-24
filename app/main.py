# app/main.py

import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import router

from model_loader import initialize_rag_resources

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s')

# Use async context manager for lifespan events (startup and shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events.

    On startup: Initializes RAG resources (LLM, retriever, chains).
    On shutdown: Can be used for cleanup if necessary.
    """
    logging.info("Application startup: Initializing RAG resources...")
    try:
        # Load models, vector store, retriever, and chains
        rag_resources = initialize_rag_resources()
        # Store resources in application state for access in routes
        app.state.rag_resources = rag_resources
        logging.info("RAG resources initialized successfully and stored in app.state.")
    except Exception as e:
        # Critical failure if resources can't load
        logging.critical(f"Failed to initialize RAG resources during startup: {e}", exc_info=True)
        # Optionally, raise the exception to prevent the app from starting
        # raise
    yield
    # --- Cleanup --- (Optional)
    # Add any cleanup logic here (e.g., closing connections)
    logging.info("Application shutdown.")

# Initialize FastAPI app with lifespan manager
app = FastAPI(
    title="Nutri-RAG Backend API",
    description="API for providing nutrition and recipe recommendations using RAG.",
    version="1.0",
    lifespan=lifespan
)

# --- CORS Configuration --- #
# Read allowed origins from environment variable
origins_str = os.getenv("ORIGINS") # Renamed for clarity
if origins_str:
    origins = [origin.strip() for origin in origins_str.split(",")]
    logging.info(f"CORS enabled for origins: {origins}")
else:
    # Default to allow Streamlit default port for local development if not set
    logging.warning("ALLOWED_ORIGINS environment variable not set. Allowing default Streamlit origin (http://localhost:8501) for development.")
    origins = ["http://localhost:8501"] # Adjust if your Streamlit runs elsewhere


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Include API routes
app.include_router(router)

# Optional: Add a root endpoint for health check or basic info
@app.get("/")
async def read_root():
    return {"message": "Nutri-RAG API is running."}

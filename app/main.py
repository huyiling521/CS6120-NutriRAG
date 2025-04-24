# app/main.py

import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import router  

from app.model_loader import initialize_rag_resources

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Application startup...")
    try:
        rag_resources = initialize_rag_resources()
        app.state.rag_resources = rag_resources
        logging.info("RAG resources initialized successfully.")
    except Exception as e:
        logging.critical(f"Failed to initialize RAG resources during startup: {e}", exc_info=True)
    yield
    logging.info("Application shutdown...")


app = FastAPI(
    title="Nutri-RAG 后端 API",
    description="提供健身营养推荐的 API 接口",
    version="1.0",
    lifespan=lifespan
)


origins_str = os.getenv("ORIGINS") # Get the env var as a string first
if origins_str:
    # Split only if the string is not None or empty
    # Also, strip whitespace from each origin in case of "origin1, origin2"
    origins = [origin.strip() for origin in origins_str.split(",")]
else:
    # Handle case where ORIGINS env var is not set or empty
    logging.warning("ORIGINS environment variable not set or empty. Allowing all origins ('*') for development. Configure properly for production.")
    origins = ["*"] # WARNING: "*" allows all origins, use specific origins in production!


app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

# 挂载路由
app.include_router(router)

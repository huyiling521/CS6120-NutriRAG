# app/routes.py
from fastapi import APIRouter, Request, HTTPException
from schemas import QueryRequest  # Import the request model
from rag_chain import full_rag_pipeline # Import the main RAG pipeline function
import logging # Import logging

router = APIRouter()

@router.post("/recommend")  # 更改路由路径
async def recommend_text(req: QueryRequest, request: Request): # 使用新的请求模型
    # 这里将调用 RAG 核心流程
    markdown_response = await full_rag_pipeline(req.query, request) # 取消调用注释
    
    return {
        "message": "成功收到请求 ✅",
        "markdown_response": markdown_response
    }

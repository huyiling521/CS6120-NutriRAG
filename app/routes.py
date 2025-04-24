# app/routes.py
from fastapi import APIRouter, Request, HTTPException
from app.schemas import QueryRequest  # Import the request model
from app.rag_chain import full_rag_pipeline # Import the main RAG pipeline function
import logging # Import logging

router = APIRouter()

@router.post("/recommend")  # 更改路由路径
async def recommend_text(req: QueryRequest, request: Request): # 使用新的请求模型

    query = req.query
    history = req.history or []

    # ✅ 打印看看收到的历史（开发调试用）
    print("--- Received History ---")
    for msg in history:
        print(f"{msg.role}: {msg.content}")
    print("------------------------")

    markdown_response = await full_rag_pipeline(req.query, req.history, request) # 取消调用注释
    
    return {
        "message": "成功收到请求 ✅",
        "markdown_response": markdown_response
    }

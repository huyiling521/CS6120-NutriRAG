# app/routes.py
from fastapi import APIRouter, Request
from app.schemas import QueryRequest  # 导入新的请求模型
# 假设 RAG 逻辑在 rag_chain.py 中
from app.rag_chain import full_rag_pipeline # 取消导入注释

router = APIRouter()

# 移除旧的 RecommendRequest
# class RecommendRequest(BaseModel):
#     goal: str
#     preferences: list[str]
#     allergies: list[str]

@router.post("/recommend")  # 更改路由路径
async def recommend_text(req: QueryRequest, request: Request): # 使用新的请求模型
    # 这里将调用 RAG 核心流程
    markdown_response = await full_rag_pipeline(req.query, request) # 取消调用注释
    
    return {
        "message": "成功收到请求 ✅",
        "markdown_response": markdown_response
    }

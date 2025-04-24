# app/routes.py
from fastapi import APIRouter
from app.schemas import QueryRequest  # 导入新的请求模型
# 假设 RAG 逻辑在 rag_chain.py 中
from app.rag_chain import full_rag_pipeline # 取消导入注释

router = APIRouter()

# 移除旧的 RecommendRequest
# class RecommendRequest(BaseModel):
#     goal: str
#     preferences: list[str]
#     allergies: list[str]

@router.post("/recommend_text")  # 更改路由路径
def recommend_text(req: QueryRequest): # 使用新的请求模型
    # 这里将调用 RAG 核心流程
    markdown_response = full_rag_pipeline(req.query) # 取消调用注释
    
    # 移除之前的占位符响应
    # markdown_response = f"### 收到请求\n查询内容：{req.query}\n\n（此处应为 RAG 生成的 Markdown 结果）"
    
    return {
        "message": "成功收到请求 ✅",
        "goal": req.goal,
        "preferences": req.preferences,
        "allergies": req.allergies
    }

# app/routes.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RecommendRequest(BaseModel):
    goal: str
    preferences: list[str]
    allergies: list[str]

@router.post("/recommend")
def recommend(req: RecommendRequest):
    # 这里调用你的 LangChain 推理逻辑即可
    return {
        "message": "成功收到请求 ✅",
        "goal": req.goal,
        "preferences": req.preferences,
        "allergies": req.allergies
    }

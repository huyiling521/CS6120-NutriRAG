# app/main.py
from fastapi import FastAPI
from app.routes import router  # 引入你定义的路由模块

app = FastAPI(
    title="Nutri-RAG 后端 API",
    description="提供健身营养推荐的 API 接口",
    version="1.0"
)

# 挂载路由
app.include_router(router)

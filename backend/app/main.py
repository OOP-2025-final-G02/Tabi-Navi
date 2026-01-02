"""
メインアプリケーションエントリーポイント
FastAPI アプリケーションの初期化と設定
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.routes import storage

app = FastAPI(
    title="AI旅行プランナー API",
    description="ユーザーの予算、興味、スケジュールに合わせて最適な旅行プランを自動生成します",
    version="0.1.0"
)

# CORS設定 - フロントエンドからのリクエストを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ストレージエンドポイント登録
app.include_router(storage.router)


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    init_db()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

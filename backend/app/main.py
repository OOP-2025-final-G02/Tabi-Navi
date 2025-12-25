"""
メインアプリケーションエントリーポイント
FastAPI アプリケーションの初期化と設定
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {"message": "AI旅行プランナー API is running", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
メインアプリケーションエントリーポイント
FastAPI アプリケーションの初期化と設定
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from .database.db import init_db
from .routes import storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # Startup イベント
    init_db()
    yield
    # Shutdown イベント
    pass


app = FastAPI(
    title="AI旅行プランナー API",
    description="ユーザーの予算、興味、スケジュールに合わせて最適な旅行プランを自動生成します",
    version="0.1.0",
    lifespan=lifespan
)

# CORS設定 - フロントエンドからのリクエストを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ストレージエンドポイント登録（APIエンドポイントを先に登録）
app.include_router(storage.router)


# フロントエンド静的ファイルを配信（最後にマウント - 全パスをキャッチするため）
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path
    
    # backend ディレクトリを sys.path に追加
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

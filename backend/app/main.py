"""
メインアプリケーションエントリーポイント
FastAPI アプリケーションの初期化と設定
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
from contextlib import asynccontextmanager
from .database.db import init_db
from .routes import storage, plan
from .config import settings # 設定をインポート


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    try:
        # APIキーが読み込めているか確認（最初の数文字を表示）
        key_hint = settings.GEMINI_API_KEY[:5] if settings.GEMINI_API_KEY else "None"
        print(f"🔑 API Key Check: {key_hint}...")
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
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

# プランエンドポイント登録
app.include_router(plan.router)


# フロントエンド静的ファイルを配信（最後にマウント - 全パスをキャッチするため）
project_root = Path(__file__).resolve().parent.parent.parent
frontend_path = project_root / "frontend"

print(f"📂 Project Root: {project_root}")
print(f"📂 Frontend Path: {frontend_path}")

# favicon.ico 404エラー回避用（アイコンがない場合は204 No Contentを返す）
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# ルートパスで index.html を明示的に返す
@app.get("/")
async def serve_index():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "index.html not found", "path": str(index_file)}, 404

if frontend_path.exists():
    print("✅ Frontend directory found. Mounting static files.")
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
else:
    print("⚠️ Frontend directory NOT found. Web interface will not be available.")


if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path
    
    # backend ディレクトリを sys.path に追加
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

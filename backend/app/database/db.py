"""
SQLiteデータベース設定
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
from app.models.db_models import Base

# データベースパス
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database.db"

# SQLAlchemy エンジン作成
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # SQLログ出力（開発時はTrue）
)

# セッション作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    依存性注入用: データベースセッション取得
    
    Usage in FastAPI:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    データベース初期化
    - テーブルが存在しない場合は作成
    - 既存テーブルには影響なし
    """
    print("🔧 データベース初期化中...")
    
    # データベースディレクトリ作成
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # テーブル作成
    Base.metadata.create_all(bind=engine)
    
    # 確認
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"✅ テーブル作成完了: {', '.join(tables)}")
    else:
        print("⚠️  テーブルが作成されていません")


def cleanup_old_plans(days: int = 365) -> int:
    """
    古いプランを自動削除
    
    Args:
        days (int): この日数以上古いプランを削除（デフォルト: 365日）
        
    Returns:
        int: 削除したプラン数
    """
    from datetime import datetime, timedelta
    from app.models.db_models import TravelPlanDB
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 削除対象を検索
        old_plans = db.query(TravelPlanDB).filter(
            TravelPlanDB.created_at < cutoff_date
        ).all()
        
        delete_count = len(old_plans)
        
        # 削除実行
        for plan in old_plans:
            db.delete(plan)
        
        db.commit()
        
        print(f"✅ 削除完了: {delete_count}個の古いプランを削除しました")
        return delete_count
        
    except Exception as e:
        db.rollback()
        print(f"❌ エラー: {str(e)}")
        return 0
    finally:
        db.close()


def get_db_status() -> dict:
    """
    データベースの状態確認
    
    Returns:
        dict: テーブル情報など
    """
    inspector = inspect(engine)
    
    return {
        "database": str(DB_PATH),
        "exists": DB_PATH.exists(),
        "tables": inspector.get_table_names(),
        "table_count": len(inspector.get_table_names())
    }

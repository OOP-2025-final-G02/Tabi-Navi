# データベース実装ガイド - SQLiteと編集履歴管理

**対象**: データベース・バックエンド基盤 担当者  
**最終更新**: 2025年12月27日

---

## 📌 概要

本ドキュメントは、SQLiteデータベースとプラン管理の実装について、詳細な手順と仕様を記載しています。

### 主要責務
- SQLite データベース設計・構築
- プラン永続化 と取得
- 編集履歴の記録・管理
- ス토レージエンドポイント実装
- プラン自動削除 ロジック

---

## 🏗️ バックエンド ディレクトリ構造

```
backend/
├── app/
│   ├── main.py                           # ✅ FastAPI メインファイル
│   ├── models/
│   │   ├── __init__.py
│   │   ├── travel_plan.py                # TravelPlan / TravelInput
│   │   └── db_models.py                  # ✨ SQLAlchemy ORM（責務: あなた）
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── plan.py                       # プラン生成・編集（AI担当が主）
│   │   └── storage.py                    # ✨ ストレージエンドポイント（責務: あなた）
│   ├── services/
│   │   ├── __init__.py
│   │   ├── plan_generator.py             # AI呼び出し（AI担当）
│   │   ├── gemini_service.py             # Gemini API（AI担当）
│   │   ├── plan_storage_service.py       # ✨ DB保存ロジック（責務: あなた）
│   │   ├── history_service.py            # ✨ 編集履歴管理（責務: あなた）
│   │   └── prompts/
│   │       └── travel_plan_prompt.py     # プロンプト（AI担当）
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── json_handler.py               # JSON記録（AI担当）
│   │   ├── validators.py                 # ✅ 検証（共通）
│   │   └── exceptions.py                 # ✅ 例外定義（共通）
│   └── database/
│       ├── __init__.py                   # ✨ DB初期化（責務: あなた）
│       └── db.py                         # ✨ SQLAlchemy設定（責務: あなた）
├── config.py                             # ✅ 環境変数読み込み
├── requirements.txt                      # ✅ 依存パッケージ
├── .env.example                          # ✅ 環境変数テンプレート
├── data/
│   ├── database.db                       # ✨ SQLiteデータベース（自動作成）
│   └── gemini_logs/                      # JSON ログ（AI担当）
└── tests/
    ├── test_storage.py                   # ✨ ストレージテスト（責務: あなた）
    └── test_history.py                   # ✨ 履歴テスト（責務: あなた）
```

**凡例**:
- ✅ = すでに存在・基本実装済み
- ✨ = あなたが実装・担当する部分

---

## 🔑 必須ファイル実装詳細

### 1. `backend/app/database/db.py`

**目的**: SQLAlcheme設定とデータベース接続管理

```python
"""
SQLiteデータベース設定
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
from app.config import settings
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
```

**実装チェックリスト**:
- [ ] SQLAlchemy エンジン作成
- [ ] セッション管理
- [ ] テーブル自動作成
- [ ] エラーハンドリング
- [ ] 古いプラン削除ロジック

---

### 2. `backend/app/database/__init__.py`

```python
"""
データベース パッケージ初期化
"""

from .db import get_db, init_db, cleanup_old_plans, get_db_status

__all__ = ["get_db", "init_db", "cleanup_old_plans", "get_db_status"]
```

---

### 3. `backend/app/models/db_models.py`

**目的**: SQLAlchemy ORM モデル定義

```python
"""
SQLAlchemy ORM データモデル
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class TravelPlanDB(Base):
    """
    旅行プラン永続化モデル
    
    保存内容:
    - 入力条件（origin, destination, dates など）
    - 生成されたスケジュール全体
    - 総費用、総所要時間
    - 作成・更新タイムスタンプ
    """
    
    __tablename__ = "travel_plans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 入力条件（JSON保存）
    input_data = Column(JSON, nullable=False)
    
    # 生成されたスケジュール
    schedules = Column(JSON, nullable=False)
    
    # 集計データ
    total_cost = Column(Integer, nullable=False, default=0)
    total_duration = Column(Integer, nullable=False, default=0)  # 分単位
    
    # タイムスタンプ
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<TravelPlanDB(plan_id={self.plan_id}, created_at={self.created_at})>"
    
    def to_dict(self):
        """辞書形式に変換"""
        return {
            "plan_id": self.plan_id,
            "input_data": self.input_data,
            "schedules": self.schedules,
            "total_cost": self.total_cost,
            "total_duration": self.total_duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TimelineItemHistory(Base):
    """
    アイテム編集履歴モデル
    
    各編集操作（update, delete, insert）を記録
    復元が必要な場合はこのテーブルから復元
    """
    
    __tablename__ = "timeline_item_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), nullable=False, index=True)
    
    # 編集対象の位置
    day = Column(Integer, nullable=False)  # 旅行の何日目か
    item_index = Column(Integer, nullable=False)  # その日のタイムライン内のインデックス
    
    # 編集内容
    operation_type = Column(
        String(20),
        nullable=False,
        # "update" = フィールド変更
        # "delete" = アイテム削除
        # "insert" = アイテム追加
    )
    
    original_data = Column(JSON)  # 変更前データ（deleteなら削除前）
    updated_data = Column(JSON)   # 変更後データ（insertなら追加データ）
    
    # メタデータ
    field_changed = Column(String(50))  # 変更されたフィールド名（update時のみ）
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<TimelineItemHistory(plan_id={self.plan_id}, operation={self.operation_type}, created_at={self.created_at})>"
    
    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "day": self.day,
            "item_index": self.item_index,
            "operation_type": self.operation_type,
            "field_changed": self.field_changed,
            "original_data": self.original_data,
            "updated_data": self.updated_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
```

**実装チェックリスト**:
- [ ] Base クラス定義
- [ ] TravelPlanDB テーブル
- [ ] TimelineItemHistory テーブル
- [ ] JSON カラム設定
- [ ] インデックス設定
- [ ] to_dict() メソッド実装

---

### 4. `backend/app/services/plan_storage_service.py`

**目的**: プランの保存・取得・更新ロジック

```python
"""
プラン保存・取得サービス
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.db_models import TravelPlanDB, TimelineItemHistory
from app.models.travel_plan import TravelPlan
from app.utils.exceptions import PlanNotFoundError, DatabaseError


class PlanStorageService:
    """プラン永続化管理"""
    
    @staticmethod
    async def save_plan(plan: TravelPlan, db: Session) -> str:
        """
        プランをDBに保存
        
        Args:
            plan (TravelPlan): 保存するプラン
            db (Session): DBセッション
            
        Returns:
            str: plan_id
            
        Raises:
            DatabaseError: DB操作エラー
        """
        try:
            db_plan = TravelPlanDB(
                plan_id=plan.plan_id,
                input_data=plan.input_data,
                schedules=plan.schedules,
                total_cost=plan.total_cost,
                total_duration=plan.total_duration,
                created_at=plan.created_at or datetime.now()
            )
            
            db.add(db_plan)
            db.commit()
            db.refresh(db_plan)
            
            return db_plan.plan_id
            
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"プラン保存エラー: {str(e)}")
    
    @staticmethod
    async def get_plan(plan_id: str, db: Session) -> TravelPlan:
        """
        プランをDBから取得
        
        Args:
            plan_id (str): プラン ID
            db (Session): DBセッション
            
        Returns:
            TravelPlan: 取得したプラン
            
        Raises:
            PlanNotFoundError: プラン未検出時
        """
        try:
            db_plan = db.query(TravelPlanDB).filter(
                TravelPlanDB.plan_id == plan_id
            ).first()
            
            if not db_plan:
                raise PlanNotFoundError(f"プラン未検出: {plan_id}")
            
            # DBモデルからPydanticモデルに変換
            return TravelPlan(
                plan_id=db_plan.plan_id,
                input_data=db_plan.input_data,
                schedules=db_plan.schedules,
                total_cost=db_plan.total_cost,
                total_duration=db_plan.total_duration,
                created_at=db_plan.created_at
            )
            
        except PlanNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"プラン取得エラー: {str(e)}")
    
    @staticmethod
    async def get_all_plans(
        db: Session,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        """
        保存済みプラン一覧を取得（最新順）
        
        Args:
            db (Session): DBセッション
            limit (int): 取得件数
            offset (int): オフセット
            
        Returns:
            List[dict]: プラン一覧
        """
        try:
            db_plans = db.query(TravelPlanDB).order_by(
                desc(TravelPlanDB.created_at)
            ).limit(limit).offset(offset).all()
            
            return [plan.to_dict() for plan in db_plans]
            
        except Exception as e:
            raise DatabaseError(f"プラン一覧取得エラー: {str(e)}")
    
    @staticmethod
    async def update_plan(
        plan_id: str,
        updated_plan: TravelPlan,
        db: Session
    ) -> bool:
        """
        プラン情報を更新
        
        Args:
            plan_id (str): プラン ID
            updated_plan (TravelPlan): 更新内容
            db (Session): DBセッション
            
        Returns:
            bool: 更新成功時 True
            
        Raises:
            PlanNotFoundError: プラン未検出時
            DatabaseError: DB操作エラー
        """
        try:
            db_plan = db.query(TravelPlanDB).filter(
                TravelPlanDB.plan_id == plan_id
            ).first()
            
            if not db_plan:
                raise PlanNotFoundError(f"プラン未検出: {plan_id}")
            
            # 更新実行
            db_plan.schedules = updated_plan.schedules
            db_plan.total_cost = updated_plan.total_cost
            db_plan.total_duration = updated_plan.total_duration
            db_plan.updated_at = datetime.now()
            
            db.commit()
            return True
            
        except PlanNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"プラン更新エラー: {str(e)}")
    
    @staticmethod
    async def delete_plan(plan_id: str, db: Session) -> bool:
        """
        プランを削除（編集履歴も一緒に削除）
        
        Args:
            plan_id (str): プラン ID
            db (Session): DBセッション
            
        Returns:
            bool: 削除成功時 True
            
        Raises:
            PlanNotFoundError: プラン未検出時
        """
        try:
            # 編集履歴を削除
            db.query(TimelineItemHistory).filter(
                TimelineItemHistory.plan_id == plan_id
            ).delete()
            
            # プランを削除
            result = db.query(TravelPlanDB).filter(
                TravelPlanDB.plan_id == plan_id
            ).delete()
            
            db.commit()
            
            if result == 0:
                raise PlanNotFoundError(f"プラン未検出: {plan_id}")
            
            return True
            
        except PlanNotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"プラン削除エラー: {str(e)}")
    
    @staticmethod
    async def count_plans(db: Session) -> int:
        """
        保存済みプラン数を取得
        
        Args:
            db (Session): DBセッション
            
        Returns:
            int: プラン数
        """
        try:
            return db.query(TravelPlanDB).count()
        except Exception as e:
            raise DatabaseError(f"プラン数取得エラー: {str(e)}")


# グローバルインスタンス
plan_storage_service = PlanStorageService()
```

**実装チェックリスト**:
- [ ] save_plan() 実装
- [ ] get_plan() 実装
- [ ] update_plan() 実装
- [ ] delete_plan() 実装
- [ ] get_all_plans() 実装
- [ ] エラーハンドリング

---

### 5. `backend/app/services/history_service.py`

**目的**: 編集履歴の記録・管理

```python
"""
編集履歴管理サービス
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.db_models import TimelineItemHistory
from app.utils.exceptions import DatabaseError


class HistoryService:
    """編集履歴管理"""
    
    @staticmethod
    async def record_edit(
        plan_id: str,
        day: int,
        item_index: int,
        operation_type: str,  # "update" / "delete" / "insert"
        original_data: Optional[dict] = None,
        updated_data: Optional[dict] = None,
        field_changed: Optional[str] = None,
        db: Session = None
    ) -> str:
        """
        編集操作を履歴に記録
        
        Args:
            plan_id (str): プラン ID
            day (int): 旅行の何日目
            item_index (int): タイムラインのインデックス
            operation_type (str): "update" / "delete" / "insert"
            original_data (dict): 変更前データ（delete時は削除前）
            updated_data (dict): 変更後データ（insert時は追加データ）
            field_changed (str): 変更フィールド名（update時のみ）
            db (Session): DBセッション
            
        Returns:
            str: 作成した履歴 ID
            
        Raises:
            DatabaseError: DB操作エラー
        """
        try:
            history = TimelineItemHistory(
                plan_id=plan_id,
                day=day,
                item_index=item_index,
                operation_type=operation_type,
                original_data=original_data,
                updated_data=updated_data,
                field_changed=field_changed,
                created_at=datetime.now()
            )
            
            db.add(history)
            db.commit()
            db.refresh(history)
            
            return history.id
            
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"履歴記録エラー: {str(e)}")
    
    @staticmethod
    async def get_history(
        plan_id: str,
        db: Session
    ) -> List[dict]:
        """
        プランの編集履歴を全て取得（時系列）
        
        Args:
            plan_id (str): プラン ID
            db (Session): DBセッション
            
        Returns:
            List[dict]: 編集履歴リスト
        """
        try:
            histories = db.query(TimelineItemHistory).filter(
                TimelineItemHistory.plan_id == plan_id
            ).order_by(desc(TimelineItemHistory.created_at)).all()
            
            return [h.to_dict() for h in histories]
            
        except Exception as e:
            raise DatabaseError(f"履歴取得エラー: {str(e)}")
    
    @staticmethod
    async def get_history_by_day(
        plan_id: str,
        day: int,
        db: Session
    ) -> List[dict]:
        """
        特定の日の編集履歴を取得
        
        Args:
            plan_id (str): プラン ID
            day (int): 日付
            db (Session): DBセッション
            
        Returns:
            List[dict]: 編集履歴リスト
        """
        try:
            histories = db.query(TimelineItemHistory).filter(
                TimelineItemHistory.plan_id == plan_id,
                TimelineItemHistory.day == day
            ).order_by(desc(TimelineItemHistory.created_at)).all()
            
            return [h.to_dict() for h in histories]
            
        except Exception as e:
            raise DatabaseError(f"履歴取得エラー: {str(e)}")
    
    @staticmethod
    async def get_history_count(plan_id: str, db: Session) -> int:
        """
        プランの編集回数をカウント
        
        Args:
            plan_id (str): プラン ID
            db (Session): DBセッション
            
        Returns:
            int: 編集回数
        """
        try:
            return db.query(TimelineItemHistory).filter(
                TimelineItemHistory.plan_id == plan_id
            ).count()
            
        except Exception as e:
            raise DatabaseError(f"履歴数カウントエラー: {str(e)}")
    
    @staticmethod
    async def clear_history(plan_id: str, db: Session) -> int:
        """
        プランの編集履歴を全クリア
        
        Args:
            plan_id (str): プラン ID
            db (Session): DBセッション
            
        Returns:
            int: 削除した履歴数
        """
        try:
            result = db.query(TimelineItemHistory).filter(
                TimelineItemHistory.plan_id == plan_id
            ).delete()
            
            db.commit()
            return result
            
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"履歴クリアエラー: {str(e)}")
    
    @staticmethod
    async def get_recent_history(
        plan_id: str,
        limit: int = 10,
        db: Session = None
    ) -> List[dict]:
        """
        最近の編集履歴を取得
        
        Args:
            plan_id (str): プラン ID
            limit (int): 取得件数
            db (Session): DBセッション
            
        Returns:
            List[dict]: 編集履歴リスト
        """
        try:
            histories = db.query(TimelineItemHistory).filter(
                TimelineItemHistory.plan_id == plan_id
            ).order_by(
                desc(TimelineItemHistory.created_at)
            ).limit(limit).all()
            
            return [h.to_dict() for h in histories]
            
        except Exception as e:
            raise DatabaseError(f"最近の履歴取得エラー: {str(e)}")


# グローバルインスタンス
history_service = HistoryService()
```

**実装チェックリスト**:
- [ ] record_edit() 実装
- [ ] get_history() 実装
- [ ] get_history_by_day() 実装
- [ ] get_history_count() 実装
- [ ] clear_history() 実装

---

### 6. `backend/app/routes/storage.py`

**目的**: ストレージ管理エンドポイント

```python
"""
プラン保存・履歴管理エンドポイント
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.plan_storage_service import plan_storage_service
from app.services.history_service import history_service
from app.utils.exceptions import PlanNotFoundError, DatabaseError

router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.get("/plans/history")
async def get_plans_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    保存済みプラン一覧取得（最新順）
    
    Query Parameters:
        limit (int): 取得件数（1-100、デフォルト: 10）
        offset (int): オフセット（デフォルト: 0）
    
    Response:
        {
            "success": true,
            "data": [
                {
                    "plan_id": "uuid",
                    "input_data": {...},
                    "total_cost": 50000,
                    "total_duration": 1440,
                    "created_at": "2025-12-27T12:00:00",
                    "updated_at": "2025-12-27T12:00:00"
                }
            ],
            "count": 1,
            "total": 1
        }
    """
    try:
        plans = await plan_storage_service.get_all_plans(db, limit, offset)
        total_count = await plan_storage_service.count_plans(db)
        
        return {
            "success": True,
            "data": plans,
            "count": len(plans),
            "total": total_count
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}")
async def get_plan(
    plan_id: str,
    db: Session = Depends(get_db)
):
    """
    プラン詳細取得
    
    Path Parameters:
        plan_id (str): プラン ID
    
    Response:
        {
            "success": true,
            "data": {
                "plan_id": "uuid",
                "input_data": {...},
                "schedules": [...],
                "total_cost": 50000,
                "total_duration": 1440,
                "created_at": "2025-12-27T12:00:00"
            }
        }
    """
    try:
        plan = await plan_storage_service.get_plan(plan_id, db)
        return {
            "success": True,
            "data": plan.dict()
        }
    except PlanNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
    db: Session = Depends(get_db)
):
    """
    プラン削除（編集履歴も同時削除）
    
    Path Parameters:
        plan_id (str): プラン ID
    
    Response:
        {
            "success": true,
            "message": "プランを削除しました"
        }
    """
    try:
        await plan_storage_service.delete_plan(plan_id, db)
        return {
            "success": True,
            "message": "プランを削除しました"
        }
    except PlanNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}/edit-history")
async def get_plan_history(
    plan_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    プラン編集履歴取得
    
    Path Parameters:
        plan_id (str): プラン ID
    
    Query Parameters:
        limit (int): 取得件数（デフォルト: 50）
    
    Response:
        {
            "success": true,
            "data": [
                {
                    "id": "history_id",
                    "plan_id": "uuid",
                    "day": 1,
                    "item_index": 2,
                    "operation_type": "update",
                    "field_changed": "time",
                    "original_data": {...},
                    "updated_data": {...},
                    "created_at": "2025-12-27T12:05:00"
                }
            ],
            "count": 5
        }
    """
    try:
        # プランの存在確認
        await plan_storage_service.get_plan(plan_id, db)
        
        # 履歴取得
        histories = await history_service.get_recent_history(plan_id, limit, db)
        
        return {
            "success": True,
            "data": histories,
            "count": len(histories)
        }
    except PlanNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_storage_status(db: Session = Depends(get_db)):
    """
    ストレージ状態確認
    
    Response:
        {
            "success": true,
            "data": {
                "total_plans": 5,
                "total_history_records": 25,
                "database": "/path/to/database.db"
            }
        }
    """
    try:
        from app.database.db import get_db_status
        
        total_plans = await plan_storage_service.count_plans(db)
        
        return {
            "success": True,
            "data": {
                "total_plans": total_plans,
                "database_status": get_db_status()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**実装チェックリスト**:
- [ ] GET /api/storage/plans/history
- [ ] GET /api/storage/plans/{plan_id}
- [ ] DELETE /api/storage/plans/{plan_id}
- [ ] GET /api/storage/plans/{plan_id}/edit-history
- [ ] GET /api/storage/status

---

## 🔌 環境変数設定

### `.env` ファイル例

```env
# Database
DATABASE_URL=sqlite:///./data/database.db
PLAN_AUTO_DELETE_DAYS=365

# Application
LOG_LEVEL=INFO
```

---

## 📦 必要なパッケージ

```bash
pip install sqlalchemy==2.0.45
```

または `requirements.txt` から：

```bash
pip install -r requirements.txt
```

---

## 🧪 テスト実装例

```python
"""
test_storage.py - ストレージサービステスト
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import Base, TravelPlanDB
from app.services.plan_storage_service import PlanStorageService
from app.models.travel_plan import TravelPlan
from datetime import datetime

# テスト用DB（メモリ）
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def test_db():
    """テスト用DBセッション"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.mark.asyncio
async def test_save_plan_success(test_db):
    """正常系: プラン保存"""
    plan = TravelPlan(
        plan_id="test-plan-1",
        input_data={"origin": "東京", "destination": "京都"},
        schedules=[],
        total_cost=50000,
        total_duration=1440,
        created_at=datetime.now()
    )
    
    service = PlanStorageService()
    result = await service.save_plan(plan, test_db)
    
    assert result == "test-plan-1"
    
    # DB確認
    saved_plan = test_db.query(TravelPlanDB).filter_by(plan_id="test-plan-1").first()
    assert saved_plan is not None
    assert saved_plan.total_cost == 50000


@pytest.mark.asyncio
async def test_get_plan_not_found(test_db):
    """異常系: プラン未検出"""
    service = PlanStorageService()
    
    with pytest.raises(Exception):
        await service.get_plan("nonexistent", test_db)


@pytest.mark.asyncio
async def test_get_all_plans(test_db):
    """正常系: プラン一覧取得"""
    # テストデータ追加
    for i in range(3):
        plan = TravelPlanDB(
            plan_id=f"plan-{i}",
            input_data={},
            schedules=[],
            total_cost=10000 * (i + 1),
            total_duration=1440
        )
        test_db.add(plan)
    test_db.commit()
    
    service = PlanStorageService()
    plans = await service.get_all_plans(test_db, limit=10, offset=0)
    
    assert len(plans) == 3


@pytest.mark.asyncio
async def test_delete_plan_success(test_db):
    """正常系: プラン削除"""
    # テストデータ追加
    plan = TravelPlanDB(
        plan_id="test-delete",
        input_data={},
        schedules=[],
        total_cost=50000,
        total_duration=1440
    )
    test_db.add(plan)
    test_db.commit()
    
    service = PlanStorageService()
    result = await service.delete_plan("test-delete", test_db)
    
    assert result is True
    
    # 確認
    deleted = test_db.query(TravelPlanDB).filter_by(plan_id="test-delete").first()
    assert deleted is None
```

---

## 🔍 トラブルシューティング

### エラー: `database.db ファイルが見つからない`
```
→ backend/data/ ディレクトリが存在するか確認
→ init_db() が呼び出されているか確認（main.py）
```

### エラー: `テーブルが作成されていない`
```
→ Base.metadata.create_all() が実行されているか確認
→ SQLAlchemy エンジンの接続を確認
```

### エラー: `外部キー制約エラー`
```
→ SQLite の PRAGMA foreign_keys = ON を確認
→ 削除順序を確認（計画 → 履歴の順番）
```

### エラー: `セッションが閉じている`
```
→ Depends(get_db) を使用してセッション管理
→ try-finally で確実に close() を呼び出す
```

---

## 📝 チェックリスト

実装完了時の確認事項:

- [ ] `db.py` 実装完了
- [ ] `db_models.py` 実装完了
- [ ] `plan_storage_service.py` 実装完了
- [ ] `history_service.py` 実装完了
- [ ] `storage.py` ルート実装完了
- [ ] テーブル自動作成確認
- [ ] テストコード実装・実行
- [ ] 古いプラン削除ロジック実装
- [ ] エラーハンドリング実装
- [ ] IndexedDB 連携用JSON形式確認

---

**作成者**: バックエンド実装チーム (DB・ストレージ担当)  
**質問・相談**: AI担当者と共有事項は IMPLEMENTATION_GUIDE.md を参照

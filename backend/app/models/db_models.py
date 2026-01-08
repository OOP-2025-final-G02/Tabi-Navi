"""
SQLAlchemy ORM データモデル
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON
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

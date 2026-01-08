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

"""
プラン保存・取得サービス
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.db_models import TravelPlanDB, TimelineItemHistory
from ..models.travel_plan import TravelPlan
from ..utils.exceptions import PlanNotFoundError, DatabaseError


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
                schedules=[s.dict() for s in plan.schedules],
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
            db_plan.schedules = [s.dict() for s in updated_plan.schedules]
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

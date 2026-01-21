"""
プラン保存・履歴管理エンドポイント
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..database.db import get_db
from ..models.travel_plan import TravelPlan
from ..services.plan_storage_service import plan_storage_service
from ..services.history_service import history_service
from ..utils.exceptions import PlanNotFoundError, DatabaseError

router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.post("/plans")
async def save_plan(
    plan: TravelPlan,
    db: Session = Depends(get_db)
):
    """
    プランを保存（新規作成または更新）
    フロントエンドの「保存」ボタン押下時に呼び出されます。
    """
    try:
        # 既に存在するか確認
        try:
            await plan_storage_service.get_plan(plan.plan_id, db)
            # 存在する場合は更新
            await plan_storage_service.update_plan(plan.plan_id, plan, db)
            message = "プランを更新しました"
        except PlanNotFoundError:
            # 存在しない場合は新規保存
            await plan_storage_service.save_plan(plan, db)
            message = "プランを保存しました"
            
        return {
            "success": True,
            "message": message,
            "data": {"plan_id": plan.plan_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存エラー: {str(e)}")


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
        from ..database.db import get_db_status
        
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

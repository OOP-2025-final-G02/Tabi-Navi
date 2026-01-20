"""
旅行プラン生成関連のAPIルート
"""

from fastapi import APIRouter, HTTPException
import logging
from typing import List
from app.models.travel_plan import TravelInput, TravelPlan
from app.services.plan_generator import get_plan_generator
from app.utils.exceptions import GeminiAPIError, ValidationError

router = APIRouter(prefix="/api/plans", tags=["plans"])
logger = logging.getLogger(__name__)


@router.post("", response_model=TravelPlan)
async def generate_plan(travel_input: TravelInput) -> TravelPlan:
    """
    旅行プランを生成
    
    Args:
        travel_input (TravelInput): 旅行条件入力
        
    Returns:
        TravelPlan: 生成された旅行プラン
        
    Raises:
        HTTPException: プラン生成エラー時
    """
    try:
        plan_generator = get_plan_generator()
        travel_plan = await plan_generator.generate_plan(travel_input)
        return travel_plan
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"入力データ検証エラー: {str(e)}"
        )
    except GeminiAPIError as e:
        error_msg = str(e)
        logger.error(f"Gemini API Error: {error_msg}")
        
        # クォータ超過（429）の場合のユーザーフレンドリーなメッセージ
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="AIサービスの利用制限（レートリミット）に達しました。しばらく時間（1分程度）を空けてから再度お試しください。"
            )
            
        raise HTTPException(
            status_code=503,
            detail=f"AI プラン生成エラー: {error_msg}"
        )
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"予期しないエラー: {type(e).__name__}: {str(e)}"
        )


@router.get("/{plan_id}", response_model=TravelPlan)
async def get_plan(plan_id: str) -> TravelPlan:
    """
    生成されたプランを取得（将来の実装用）
    
    Args:
        plan_id (str): プラン ID
        
    Returns:
        TravelPlan: 旅行プラン
    """
    # 将来的にはDBから取得
    raise HTTPException(
        status_code=501,
        detail="プラン取得機能は未実装です"
    )

"""
AI旅行プラン生成サービス
"""

import uuid
from datetime import datetime
from typing import Optional
from app.models.travel_plan import TravelPlan, TravelInput, DaySchedule
from app.services.gemini_service import get_gemini_service
from app.services.prompts.travel_plan_prompt import parse_gemini_response, validate_plan_structure
from app.utils.exceptions import GeminiAPIError, ValidationError


class PlanGeneratorService:
    """プラン生成サービス"""
    
    def __init__(self):
        """初期化"""
        self.gemini_service = get_gemini_service()
    
    async def generate_plan(self, travel_input: TravelInput) -> TravelPlan:
        """
        Gemini AIを使用して旅行プランを生成
        
        Args:
            travel_input (TravelInput): 旅行条件
            
        Returns:
            TravelPlan: 生成されたプラン
            
        Raises:
            GeminiAPIError: Gemini API エラー
            ValidationError: データ検証エラー
        """
        # プラン ID を生成
        plan_id = str(uuid.uuid4())
        
        try:
            # Gemini API を呼び出し
            ai_response = await self.gemini_service.generate_travel_plan(
                travel_input,
                plan_id
            )
            
            # レスポンスをパース
            plan_data = parse_gemini_response(str(ai_response))
            
            # 構造を検証
            validate_plan_structure(plan_data)
            
            # TravelPlan モデルに変換
            travel_plan = self._convert_to_travel_plan(
                plan_id,
                travel_input,
                plan_data
            )
            
            return travel_plan
            
        except GeminiAPIError as e:
            raise GeminiAPIError(f"プラン生成失敗: {str(e)}")
        except (ValueError, ValidationError) as e:
            raise ValidationError(f"データ検証エラー: {str(e)}")
    
    def _convert_to_travel_plan(
        self,
        plan_id: str,
        travel_input: TravelInput,
        plan_data: dict
    ) -> TravelPlan:
        """
        AI生成データをTravelPlanモデルに変換
        
        Args:
            plan_id (str): プラン ID
            travel_input (TravelInput): 入力データ
            plan_data (dict): AI生成データ
            
        Returns:
            TravelPlan: 変換済みプラン
        """
        # DaySchedule オブジェクトを構築
        schedules = []
        for day_data in plan_data.get('schedules', []):
            schedule = DaySchedule(**day_data)
            schedules.append(schedule)
        
        # 合計費用と時間を計算
        total_cost = plan_data.get('total_cost', 0)
        total_duration = plan_data.get('total_duration', 0)
        
        return TravelPlan(
            plan_id=plan_id,
            input_data=travel_input.dict(),
            schedules=schedules,
            total_cost=total_cost,
            total_duration=total_duration,
            created_at=datetime.now()
        )


# グローバルインスタンス
_plan_generator = PlanGenerator()


def get_plan_generator() -> PlanGeneratorService:
    """プランジェネレーター インスタンスを取得"""
    global _plan_generator
    if _plan_generator is None:
        _plan_generator = PlanGeneratorService()
    return _plan_generator


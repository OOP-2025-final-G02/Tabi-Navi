"""
バリデーション関数
"""

from datetime import datetime
from ..models.travel_plan import TravelInput
from .exceptions import ValidationError


def validate_travel_input(data: dict) -> bool:
    """
    旅行入力データを検証
    
    Args:
        data (dict): 検証対象のデータ
        
    Returns:
        bool: 検証成功時 True
        
    Raises:
        ValidationError: バリデーション失敗時
    """
    # 必須フィールド確認
    required_fields = ["origin", "destination", "start_date", "end_date", "budget"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"必須フィールド '{field}' がありません")
    
    # 日付形式確認
    try:
        start = datetime.strptime(data["start_date"], "%Y-%m-%d")
        end = datetime.strptime(data["end_date"], "%Y-%m-%d")
    except ValueError:
        raise ValidationError("日付形式は YYYY-MM-DD である必要があります")
    
    # 日付順序確認
    if start >= end:
        raise ValidationError("開始日は終了日より前である必要があります")
    
    # 予算確認
    if not isinstance(data["budget"], (int, float)) or data["budget"] <= 0:
        raise ValidationError("予算は正の数値である必要があります")
    
    return True


def validate_plan_id(plan_id: str) -> bool:
    """
    プラン ID を検証
    
    Args:
        plan_id (str): プラン ID
        
    Returns:
        bool: 検証成功時 True
        
    Raises:
        ValidationError: バリデーション失敗時
    """
    if not plan_id or len(plan_id.strip()) == 0:
        raise ValidationError("プラン ID は空にできません")
    
    return True

"""
旅行プラン関連のデータモデル
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class TravelInput(BaseModel):
    """旅行入力条件"""
    origin: str = Field(..., description="出発地")
    destination: str = Field(..., description="目的地")
    start_date: str = Field(..., description="開始日（YYYY-MM-DD形式）")
    end_date: str = Field(..., description="終了日（YYYY-MM-DD形式）")
    budget: int = Field(..., description="予算（円）")
    interests: List[str] = Field(default_factory=list, description="興味・関心のキーワード")
    additional_notes: Optional[str] = Field(None, description="追加の要望")

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "東京",
                "destination": "京都",
                "start_date": "2025-01-01",
                "end_date": "2025-01-05",
                "budget": 100000,
                "interests": ["寺院", "グルメ"],
                "additional_notes": "駅から近い場所希望"
            }
        }


class TimelineItem(BaseModel):
    """タイムラインアイテム"""
    time: str = Field(..., description="時刻（HH:MM形式）")
    activity: str = Field(..., description="活動内容")
    location: Optional[str] = Field(None, description="場所")
    cost: int = Field(default=0, description="費用（円）")
    duration: int = Field(default=0, description="所要時間（分）")
    notes: Optional[str] = Field(None, description="備考")

    class Config:
        json_schema_extra = {
            "example": {
                "time": "09:00",
                "activity": "清水寺参拝",
                "location": "京都市東山区",
                "cost": 600,
                "duration": 60,
                "notes": "朝一番がおすすめ"
            }
        }


class DaySchedule(BaseModel):
    """1日のスケジュール"""
    day: int = Field(..., description="旅行の何日目か（1以上）")
    date: str = Field(..., description="日付（YYYY-MM-DD形式）")
    timeline: List[TimelineItem] = Field(default_factory=list, description="タイムライン")
    daily_cost: int = Field(default=0, description="1日の総費用")
    daily_duration: int = Field(default=0, description="1日の総所要時間（分）")

    class Config:
        json_schema_extra = {
            "example": {
                "day": 1,
                "date": "2025-01-01",
                "timeline": [
                    {
                        "time": "09:00",
                        "activity": "清水寺参拝",
                        "location": "京都市東山区",
                        "cost": 600,
                        "duration": 60
                    }
                ],
                "daily_cost": 5000,
                "daily_duration": 480
            }
        }


class TravelPlan(BaseModel):
    """旅行プラン全体"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="プラン ID")
    input_data: Dict[str, Any] = Field(..., description="入力条件（JSON形式）")
    schedules: List[DaySchedule] = Field(default_factory=list, description="日程スケジュール")
    total_cost: int = Field(default=0, description="総費用（円）")
    total_duration: int = Field(default=0, description="総所要時間（分）")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="作成日時")

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "550e8400-e29b-41d4-a716-446655440000",
                "input_data": {
                    "origin": "東京",
                    "destination": "京都",
                    "budget": 100000
                },
                "schedules": [],
                "total_cost": 50000,
                "total_duration": 1440,
                "created_at": "2025-01-01T12:00:00"
            }
        }

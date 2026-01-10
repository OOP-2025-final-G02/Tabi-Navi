"""
旅行プラン生成用プロンプト
"""

from typing import List
import json
from ...models.travel_plan import TravelInput


def create_travel_prompt(travel_input: TravelInput) -> str:
    """
    旅行プラン生成用プロンプト作成
    
    Args:
        travel_input (TravelInput): 旅行条件
        
    Returns:
        str: Gemini API用プロンプト
    """
    
    prompt = f"""
あなたは旅行プランナーのAIアシスタントです。以下の条件に基づいて、詳細な旅行プランを生成してください。

## 旅行条件

- **出発地**: {travel_input.origin}
- **目的地**: {travel_input.destination}
- **出発日**: {travel_input.start_date}
- **帰宅日**: {travel_input.end_date}
- **予算**: ¥{travel_input.budget:,}
- **旅行者数**: {travel_input.travelers}人
- **興味分野**: {', '.join(travel_input.interests)}
- **必訪問地**: {travel_input.must_visit}

## 要求事項

1. 出発地から目的地への移動手段を考慮する
2. 各日の朝から夜までのタイムラインを作成
3. 食事（朝食・昼食・夕食）も含める
4. 移動時間を考慮して時刻を設定
5. 予算内に収まるように費用配分
6. 各スポット/アクティビティの説明を100文字以内で記載

## 出力形式

以下のJSON形式で、正確に返してください。JSONのみを返してください。他の説明は不要です。

```json
{{
  "daily_schedules": [
    {{
      "day": 1,
      "date": "2025-12-26",
      "timeline": [
        {{
          "time": "08:00",
          "type": "meal",
          "name": "朝食 - ホテルのレストラン",
          "category": "グルメ",
          "duration": 30,
          "cost": 1500,
          "description": "ホテルのビュッフェレストランで朝食。"
        }},
        {{
          "time": "09:30",
          "type": "transportation",
          "name": "レンタカー移動",
          "category": "移動",
          "duration": 60,
          "cost": 5000,
          "method": "レンタカー",
          "description": "ホテルからレンタカーでメインスポットへ移動"
        }},
        {{
          "time": "10:30",
          "type": "spot",
          "name": "観光スポット名",
          "category": "観光",
          "duration": 120,
          "cost": 1000,
          "latitude": 26.1955,
          "longitude": 127.6747,
          "description": "観光スポットの説明（100文字以内）"
        }}
      ],
      "daily_cost": 7500
    }},
    {{
      "day": 2,
      "date": "2025-12-27",
      "timeline": [
        ...
      ],
      "daily_cost": 8000
    }}
  ],
  "summary": {{
    "total_cost": 50000,
    "total_duration_minutes": 1440,
    "highlights": ["必訪問地を含めた主要観光スポット3選"],
    "tips": ["移動時間に気をつけてください"]
  }}
}}
```

## 重要な注意事項

- 時刻は必ず HH:MM 形式（24時間制）
- 費用は全て日本円（￥）
- `duration` は分単位
- `type` は: "meal", "spot", "transportation" のいずれか
- すべての時刻が論理的に流れるように調整
- 予算合計が指定予算を超えない

旅行プランの生成を開始してください。
"""
    
    return prompt.strip()


def parse_gemini_response(response_text: str) -> dict:
    """
    Gemini APIレスポンスをパース
    
    Args:
        response_text (str): Gemini APIのレスポンステキスト
        
    Returns:
        dict: パース済みJSON
        
    Raises:
        ValueError: JSON パース失敗時
    """
    try:
        # JSONブロックの抽出（```json ... ``` の場合もある）
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
        
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON パースエラー: {str(e)}\n{response_text[:200]}")


def validate_plan_structure(plan_dict: dict) -> bool:
    """
    生成プランの構造を検証
    
    Args:
        plan_dict (dict): 検証するプラン辞書
        
    Returns:
        bool: 構造が正しければTrue
        
    Raises:
        ValueError: 構造が不正な場合
    """
    required_keys = {"daily_schedules", "summary"}
    if not required_keys.issubset(plan_dict.keys()):
        raise ValueError(f"必須キーが不足: {required_keys - set(plan_dict.keys())}")
    
    if not isinstance(plan_dict["daily_schedules"], list):
        raise ValueError("daily_schedules は配列である必要があります")
    
    if len(plan_dict["daily_schedules"]) == 0:
        raise ValueError("daily_schedules が空です")
    
    return True

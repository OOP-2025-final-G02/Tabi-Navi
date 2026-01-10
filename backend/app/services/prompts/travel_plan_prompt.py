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
    interests_str = ', '.join(travel_input.interests) if travel_input.interests else "特に指定なし"
    additional_notes = travel_input.additional_notes or "特になし"
    
    prompt = f"""
あなたは旅行プランナーのAIアシスタントです。以下の条件に基づいて、詳細な旅行プランを生成してください。

## 旅行条件

- **出発地**: {travel_input.origin}
- **目的地**: {travel_input.destination}
- **開始日**: {travel_input.start_date}
- **終了日**: {travel_input.end_date}
- **予算**: ¥{travel_input.budget:,}
- **興味**: {interests_str}
- **追加要望**: {additional_notes}

## 要求事項

1. 出発地から目的地への移動手段を考慮する
2. 各日の朝から夜までのタイムラインを作成
3. 食事（朝食・昼食・夕食）も含める
4. 移動時間を考慮して時刻を設定
5. 予算内に収まるように費用配分
6. 各アクティビティの説明は簡潔に

## 出力形式

以下のJSON形式で、正確に返してください。JSONのみを返してください。

```json
{{
  "schedules": [
    {{
      "day": 1,
      "date": "{travel_input.start_date}",
      "timeline": [
        {{
          "time": "09:00",
          "activity": "朝食",
          "location": "ホテルレストラン",
          "cost": 1500,
          "duration": 30,
          "notes": "ビュッフェスタイル"
        }},
        {{
          "time": "10:30",
          "activity": "観光スポット名",
          "location": "目的地",
          "cost": 1000,
          "duration": 120,
          "notes": "朝一番がおすすめ"
        }}
      ],
      "daily_cost": 3000,
      "daily_duration": 480
    }}
  ],
  "total_cost": {travel_input.budget},
  "total_duration": 1440
}}
```

## 重要な注意事項

- 時刻は必ず HH:MM 形式（24時間制）
- 費用は全て日本円（￥）
- `duration` は分単位
- 予算合計が指定予算を超えない
- 日数は {(travel_input.end_date)} - {(travel_input.start_date)} から計算

旅行プランの生成を開始してください。
"""
    
    return prompt.strip()

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
    required_keys = {"schedules"}
    if not required_keys.issubset(plan_dict.keys()):
        raise ValueError(f"必須キーが不足: {required_keys - set(plan_dict.keys())}")
    
    if not isinstance(plan_dict["schedules"], list):
        raise ValueError("schedules は配列である必要があります")
    
    if len(plan_dict["schedules"]) == 0:
        raise ValueError("schedules が空です")
    
    return True

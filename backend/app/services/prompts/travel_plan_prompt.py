"""
旅行プラン生成用プロンプト
"""

from typing import List
import json
from datetime import datetime
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
    
    # 日数を計算
    start = datetime.strptime(travel_input.start_date, "%Y-%m-%d")
    end = datetime.strptime(travel_input.end_date, "%Y-%m-%d")
    num_days = (end - start).days + 1
    
    prompt = f"""あなたは旅行プランナーです。以下の条件で{num_days}日間の旅行プランをJSON形式で生成してください。

## 旅行条件
出発地: {travel_input.origin}
目的地: {travel_input.destination}
開始日: {travel_input.start_date}
終了日: {travel_input.end_date}
日数: {num_days}日間
予算: ¥{travel_input.budget:,}
興味: {interests_str}
追加要望: {additional_notes}

## 必須要件
1. 各日は朝食・観光・昼食・観光・夕食を含める
2. 時刻はHH:MM形式（24時間制）
3. 費用は日本円で記載
4. durationは分単位
5. 予算内に収める

## 出力形式
必ず以下のJSON形式のみを返してください。説明文は一切含めないでください。

{{
  "schedules": [
    {{
      "day": 1,
      "date": "{travel_input.start_date}",
      "timeline": [
        {{
          "time": "08:00",
          "activity": "朝食",
          "location": "ホテル",
          "cost": 1500,
          "duration": 60,
          "notes": "和定食"
        }},
        {{
          "time": "09:30",
          "activity": "観光スポット",
          "location": "{travel_input.destination}の名所",
          "cost": 1000,
          "duration": 120,
          "notes": "朝一番がおすすめ"
        }}
      ],
      "daily_cost": 10000,
      "daily_duration": 600
    }}
  ],
  "total_cost": {travel_input.budget},
  "total_duration": {num_days * 600}
}}

重要: JSONのみを返し、```json```のマーカーも含めないでください。"""
    
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
        # マークダウンのコードブロックを除去
        cleaned_text = response_text.strip()
        
        # ```json で囲まれている場合
        if "```json" in cleaned_text:
            json_str = cleaned_text.split("```json")[1].split("```")[0].strip()
        # ``` のみで囲まれている場合
        elif cleaned_text.startswith("```") and cleaned_text.endswith("```"):
            json_str = cleaned_text[3:-3].strip()
            if json_str.startswith("json"):
                json_str = json_str[4:].strip()
        # 余分なテキストがある場合、最初の { から最後の } まで抽出
        elif "{" in cleaned_text and "}" in cleaned_text:
            start_idx = cleaned_text.find("{")
            end_idx = cleaned_text.rfind("}") + 1
            json_str = cleaned_text[start_idx:end_idx]
        else:
            json_str = cleaned_text
        
        # JSONをパース
        parsed = json.loads(json_str)
        return parsed
        
    except json.JSONDecodeError as e:
        # エラー時は元のレスポンスの一部を表示
        error_context = response_text[:500] if len(response_text) > 500 else response_text
        raise ValueError(f"JSON パースエラー: {str(e)}\n\n受信したレスポンス:\n{error_context}")
    except Exception as e:
        raise ValueError(f"予期しないエラー: {str(e)}\n\nレスポンス:\n{response_text[:500]}")


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
    
    # 各スケジュールの基本構造を検証
    for i, schedule in enumerate(plan_dict["schedules"]):
        if "day" not in schedule:
            raise ValueError(f"スケジュール{i+1}に'day'キーがありません")
        if "date" not in schedule:
            raise ValueError(f"スケジュール{i+1}に'date'キーがありません")
        if "timeline" not in schedule or not isinstance(schedule["timeline"], list):
            raise ValueError(f"スケジュール{i+1}に有効な'timeline'がありません")
    
    return True
# AI連携実装ガイド - Gemini API統合

**対象**: AI・Gemini API 連携担当者  
**最終更新**: 2025年12月27日

---

## 📌 概要

本ドキュメントは、Google Gemini APIと旅行プランナーアプリケーションの連携実装について、詳細な手順と仕様を記載しています。

### 主要責務
- Gemini API との通信実装
- プロンプト設計と最適化
- AI生成結果のパース・データ変換
- リクエスト・レスポンスのログ記録

---

## 🏗️ バックエンド ディレクトリ構造

```
backend/
├── app/
│   ├── main.py                           # FastAPI メインファイル
│   ├── models/
│   │   ├── __init__.py
│   │   ├── travel_plan.py                # ✅ TravelPlan / TravelInput モデル
│   │   └── db_models.py                  # DB用ORM（DB担当）
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── plan.py                       # ✅ プラン生成・編集エンドポイント
│   │   └── storage.py                    # ストレージ（DB担当）
│   ├── services/
│   │   ├── __init__.py
│   │   ├── plan_generator.py             # ✨ AI呼び出しロジック（責務: あなた）
│   │   ├── gemini_service.py             # ✨ Gemini API通信（責務: あなた）
│   │   ├── plan_storage_service.py       # DB保存（DB担当）
│   │   ├── history_service.py            # 編集履歴（DB担当）
│   │   └── prompts/
│   │       └── travel_plan_prompt.py     # ✨ プロンプトテンプレート（責務: あなた）
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── json_handler.py               # ✨ JSON記録管理（責務: あなた）
│   │   ├── validators.py                 # 検証（共通）
│   │   └── exceptions.py                 # 例外定義（共通）
│   └── database/
│       ├── __init__.py
│       └── db.py                         # DB設定（DB担当）
├── config.py                             # ✅ 環境変数読み込み
├── requirements.txt                      # ✅ 依存パッケージ
├── .env.example                          # ✅ 環境変数テンプレート
└── data/
    └── gemini_logs/                      # ✨ Gemini JSON ログ（責務: あなた）
```

**凡例**:
- ✅ = すでに存在・基本実装済み
- ✨ = あなたが実装・担当する部分

---

## 🔑 必須ファイル実装詳細

### 1. `backend/app/services/gemini_service.py`

**目的**: Gemini APIとの通信を一元管理

```python
"""
Gemini API通信サービス
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from google.generativeai import GenerativeModel
from app.config import settings
from app.utils.exceptions import GeminiAPIError

class GeminiService:
    """Gemini API通信管理"""
    
    def __init__(self):
        self.model = GenerativeModel('gemini-pro')
        self.timeout = settings.AI_REQUEST_TIMEOUT
    
    async def call_gemini(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Gemini APIにリクエスト送信
        
        Args:
            prompt (str): プロンプト
            temperature (float): 創造性レベル (0.0-1.0)
            max_tokens (int): 最大トークン数
            
        Returns:
            Dict[str, Any]: JSON形式のレスポンス
            
        Raises:
            GeminiAPIError: API呼び出し失敗時
        """
        try:
            # タイムアウト付きでAPI呼び出し
            response = await asyncio.wait_for(
                self._call_api(prompt, temperature, max_tokens),
                timeout=self.timeout
            )
            return response
        except asyncio.TimeoutError:
            raise GeminiAPIError(f"Gemini API タイムアウト ({self.timeout}秒)")
        except Exception as e:
            raise GeminiAPIError(f"Gemini API エラー: {str(e)}")
    
    async def _call_api(
        self, 
        prompt: str, 
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """APIを実際に呼び出す（内部メソッド）"""
        response = self.model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }
        )
        
        # レスポンスをJSON化
        response_text = response.text
        return json.loads(response_text)
    
    async def generate_travel_plan(
        self, 
        travel_input, 
        plan_id: str
    ) -> Dict[str, Any]:
        """
        旅行プラン生成（高レベルAPI）
        
        Args:
            travel_input: TravelInput モデル
            plan_id (str): プラン用UUID
            
        Returns:
            Dict[str, Any]: 生成されたプラン
        """
        # プロンプト生成
        prompt = self._create_travel_prompt(travel_input)
        
        # Gemini API呼び出し
        response = await self.call_gemini(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        # ログ記録
        await self._save_api_log(plan_id, prompt, response)
        
        return response
    
    def _create_travel_prompt(self, travel_input) -> str:
        """旅行プラン用プロンプト生成"""
        from app.services.prompts.travel_plan_prompt import create_travel_prompt
        return create_travel_prompt(travel_input)
    
    async def _save_api_log(
        self, 
        plan_id: str, 
        request: str, 
        response: Dict
    ) -> None:
        """リクエスト・レスポンスをJSONファイルに記録"""
        from app.utils.json_handler import save_gemini_log
        await save_gemini_log(plan_id, request, response)


# グローバルインスタンス
gemini_service = GeminiService()
```

**実装チェックリスト**:
- [ ] Google AI Studio でAPI キー取得
- [ ] `.env` に `GEMINI_API_KEY=...` を設定
- [ ] `google-generativeai` パッケージをインストール (`pip install google-generativeai`)
- [ ] タイムアウト処理を実装
- [ ] エラーハンドリング を実装
- [ ] JSON パース の失敗時例外を処理

---

### 2. `backend/app/services/prompts/travel_plan_prompt.py`

**目的**: 構造化されたプロンプト生成

```python
"""
旅行プラン生成用プロンプト
"""

from typing import List
import json
from app.models.travel_plan import TravelInput

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
```

**実装チェックリスト**:
- [ ] JSON 出力形式を明確に指定
- [ ] Gemini の制約（トークン数など）を考慮
- [ ] プロンプト内で出力形式の例を示す
- [ ] エッジケース（少ない予算、短期間など）に対応
- [ ] レスポンス パース 関数を実装

---

### 3. `backend/app/utils/json_handler.py`

**目的**: Gemini API のリクエスト・レスポンスをログに記録

```python
"""
JSON ログ管理
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

LOGS_DIR = Path(__file__).parent.parent.parent / "data" / "gemini_logs"

async def save_gemini_log(
    plan_id: str,
    request_prompt: str,
    response_data: Dict[str, Any]
) -> None:
    """
    Gemini API のリクエスト・レスポンスをJSONファイルに保存
    
    Args:
        plan_id (str): プラン ID
        request_prompt (str): リクエストプロンプト
        response_data (Dict): レスポンスデータ
    """
    # ログディレクトリを確認
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # ファイル名: {plan_id}_{timestamp}.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = LOGS_DIR / f"{plan_id}_{timestamp}.json"
    
    # ログデータ構築
    log_data = {
        "plan_id": plan_id,
        "timestamp": datetime.now().isoformat(),
        "request": {
            "prompt": request_prompt
        },
        "response": response_data
    }
    
    # 非同期でファイルに書き込み
    await asyncio.to_thread(
        _write_json_file,
        filename,
        log_data
    )


def _write_json_file(filepath: Path, data: Dict[str, Any]) -> None:
    """
    JSON ファイルに書き込み（同期版）
    
    Args:
        filepath (Path): 書き込み先ファイルパス
        data (Dict): 書き込みデータ
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_gemini_log(plan_id: str, timestamp: str) -> Dict[str, Any]:
    """
    保存済み Gemini ログを読み込み
    
    Args:
        plan_id (str): プラン ID
        timestamp (str): タイムスタンプ
        
    Returns:
        Dict: ログデータ
    """
    filename = LOGS_DIR / f"{plan_id}_{timestamp}.json"
    
    if not filename.exists():
        raise FileNotFoundError(f"ログファイルが見つかりません: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_gemini_logs(plan_id: str) -> list:
    """
    特定のプラン ID に対するすべてのログを列挙
    
    Args:
        plan_id (str): プラン ID
        
    Returns:
        list: ログファイルのパスリスト
    """
    return sorted(LOGS_DIR.glob(f"{plan_id}_*.json"))
```

**実装チェックリスト**:
- [ ] ログディレクトリの自動作成
- [ ] 非同期ファイル書き込み
- [ ] タイムスタンプ付きファイル名
- [ ] JSON 形式での保存
- [ ] ログ読み込み機能

---

### 4. `backend/app/services/plan_generator.py`

**目的**: AI生成プランの統合

```python
"""
旅行プラン生成サービス
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from app.models.travel_plan import TravelPlan, TravelInput
from app.services.gemini_service import gemini_service
from app.services.prompts.travel_plan_prompt import parse_gemini_response, validate_plan_structure
from app.utils.exceptions import GeminiAPIError, ValidationError

class PlanGeneratorService:
    """旅行プラン生成"""
    
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
            ai_response = await gemini_service.generate_travel_plan(
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
        # 実装はdb_models.pyを参考に
        # TravelPlanモデルの構造に合わせてデータを変換
        
        total_cost = plan_data.get('summary', {}).get('total_cost', 0)
        total_duration = plan_data.get('summary', {}).get('total_duration_minutes', 0)
        
        return TravelPlan(
            plan_id=plan_id,
            input_data=travel_input.dict(),
            schedules=plan_data.get('daily_schedules', []),
            total_cost=total_cost,
            total_duration=total_duration,
            created_at=datetime.now()
        )


# グローバルインスタンス
plan_generator = PlanGeneratorService()
```

**実装チェックリスト**:
- [ ] UUID ベースの plan_id 生成
- [ ] Gemini API 呼び出し
- [ ] レスポンス パース と検証
- [ ] TravelPlan モデルへの変換
- [ ] エラーハンドリング

---

## 🔌 環境変数設定

### `.env` ファイル例

```env
# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here
AI_REQUEST_TIMEOUT=30

# Database (DB担当)
DATABASE_URL=sqlite:///./data/database.db

# Application
PLAN_AUTO_DELETE_DAYS=365
```

### 取得手順

1. [Google AI Studio](https://aistudio.google.com) にアクセス
2. 右上の「Get API key」をクリック
3. 「Create API key in new project」を選択
4. 生成されたAPIキーをコピー
5. `.env` ファイルに貼り付け

---

## 📦  必要なパッケージ

```bash
pip install google-generativeai==0.3.0
```

または `requirements.txt` から：

```bash
pip install -r requirements.txt
```

---

## 🧪 テスト実装例

```python
"""
test_gemini_service.py - Gemini サービステスト
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.gemini_service import GeminiService
from app.models.travel_plan import TravelInput
from app.utils.exceptions import GeminiAPIError


@pytest.mark.asyncio
async def test_call_gemini_success():
    """正常系: Gemini API 呼び出し成功"""
    service = GeminiService()
    
    with patch.object(service, '_call_api') as mock_api:
        mock_api.return_value = {
            "daily_schedules": [],
            "summary": {"total_cost": 50000}
        }
        
        result = await service.call_gemini("test prompt")
        
        assert result["summary"]["total_cost"] == 50000
        mock_api.assert_called_once()


@pytest.mark.asyncio
async def test_call_gemini_timeout():
    """異常系: タイムアウト"""
    service = GeminiService()
    service.timeout = 0.001  # 超短タイムアウト
    
    with patch.object(service, '_call_api', new_callable=AsyncMock) as mock_api:
        mock_api.side_effect = asyncio.sleep(1)  # 1秒待機
        
        with pytest.raises(GeminiAPIError):
            await service.call_gemini("test prompt")


@pytest.mark.asyncio
async def test_generate_travel_plan_success():
    """正常系: プラン生成成功"""
    generator = PlanGeneratorService()
    
    travel_input = TravelInput(
        origin="東京",
        destination="京都",
        start_date="2025-12-26",
        end_date="2025-12-28",
        budget=50000,
        travelers=2,
        interests=["グルメ", "歴史"],
        must_visit="清水寺"
    )
    
    # Gemini の応答をモック
    mock_response = {
        "daily_schedules": [...],
        "summary": {
            "total_cost": 50000,
            "total_duration_minutes": 1440
        }
    }
    
    with patch.object(gemini_service, 'generate_travel_plan') as mock:
        mock.return_value = mock_response
        
        result = await generator.generate_plan(travel_input)
        
        assert result.total_cost == 50000
        assert result.plan_id is not None
```

---

## 🔍 トラブルシューティング

### エラー: `GEMINI_API_KEY環境変数が設定されていません`
```
→ .env ファイルに正しい API キーが設定されているか確認
→ 環境変数が読み込まれているか確認: echo $GEMINI_API_KEY
```

### エラー: `JSON パースエラー`
```
→ Gemini APIの出力形式を確認
→ プロンプトで JSON 形式を明確に指定しているか確認
→ ログファイルからレスポンスを確認: backend/data/gemini_logs/
```

### エラー: `Gemini API タイムアウト`
```
→ AI_REQUEST_TIMEOUT の値を増やす（.env で設定）
→ ネットワーク接続を確認
→ Gemini API のステータス確認
```

### エラー: `旅行プランの構造が不正`
```
→ parse_gemini_response() の実装を確認
→ プロンプトで期待する JSON 形式を明確に指定
→ validate_plan_structure() で必須フィールドを確認
```

---

## 📝 チェックリスト

実装完了時の確認事項:

- [ ] `gemini_service.py` 実装完了
- [ ] `travel_plan_prompt.py` 実装完了
- [ ] `json_handler.py` 実装完了
- [ ] `plan_generator.py` 実装完了
- [ ] `.env` に GEMINI_API_KEY を設定
- [ ] テストコード実装・実行
- [ ] ログファイル出力確認
- [ ] エラーハンドリング実装
- [ ] README に使用手順を記載

---

**作成者**: バックエンド実装チーム (AI連携担当)  
**質問・相談**: DB担当者と共有事項は IMPLEMENTATION_GUIDE.md を参照

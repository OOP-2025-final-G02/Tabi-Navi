# 実装タスクリスト - バックエンド

生成日: 2025年12月27日

---

## 📋 プロジェクト概要

AI旅行プランナーのバックエンド実装において、以下の3つの主要機能を実装します：

1. **Gemini APIとの連携** - AIを使用した動的な旅行プラン生成
2. **プラン永続化** - SQLiteデータベースにプランを保存・管理
3. **プラン編集機能** - 生成されたプランの各要素（観光スポット、時間など）を編集

---

## 🎯 フロントエンド向けの重要な情報

### IndexedDB連携について
- **フロントエンドはIndexedDB**（ブラウザのローカルストレージ）を使用してプラン履歴を保存
- バックエンドが提供するエンドポイントにより、IndexedDBとの同期が可能
- ユーザーログイン不要で、**その端末を使用している人のデータのみ保存・表示**される
- Webのキャッシュ的に機能

### フロントエンドが実装すべき事項
- IndexedDB への プラン保存・取得処理
- 以下のバックエンドエンドポイントを呼び出し
  - `POST /api/plans/generate` - プラン生成
  - `POST /api/plans/{plan_id}/items/{item_id}/edit` - アイテム編集
  - `GET /api/plans/{plan_id}/history` - 編集履歴取得（オプション）

---

## 🔧 バックエンド実装タスク

### フェーズ1: 基礎設定

#### タスク 1-1: SQLiteデータベース設定
- **目的**: プラン保存用のDBスキーマ設定
- **詳細**:
  - `backend/app/database/` ディレクトリを作成
  - SQLAlchemy設定ファイル作成（`backend/app/database/db.py`）
  - SQLiteデータベース接続設定
  - 初期化スクリプト作成
- **成果物**:
  - `database.db` ファイルの自動生成
  - SQLAlchemy ORM設定完了

#### タスク 1-2: DBモデル定義
- **目的**: プランと編集履歴を保存するためのデータモデル
- **詳細**:
  - `backend/app/models/db_models.py` を作成
  - 以下のテーブル構造を定義:
    - **TravelPlanDB** - 生成されたプラン全体の保存
      - id (UUID, 主キー)
      - plan_id (プランのユニークID)
      - input_data (JSON形式で旅行条件を保存)
      - schedules (JSON形式で全スケジュール保存)
      - total_cost
      - total_duration
      - created_at
      - updated_at
    - **TimelineItemHistory** - 編集履歴の記録
      - id (主キー)
      - plan_id (編集対象プラン)
      - day (何日目か)
      - item_index (タイムライン内のインデックス)
      - original_data (変更前のデータをJSON保存)
      - updated_data (変更後のデータをJSON保存)
      - operation_type (値: "update", "delete", "insert")
      - created_at
- **成果物**:
  - `db_models.py` with SQLAlchemy ORM定義

#### タスク 1-3: 環境変数設定
- **目的**: 設定管理の強化
- **詳細**:
  - `backend/.env.example` を更新
    - `GEMINI_API_KEY` を追加
    - `DATABASE_URL` を追加（SQLiteのパス）
    - `AI_REQUEST_TIMEOUT` を追加（デフォルト: 30秒）
  - `backend/config.py` を拡張
    - Gemini API キー読み込み
    - DB接続文字列の読み込み
- **成果物**:
  - `.env.example` 更新
  - `config.py` 拡張

---

### フェーズ2: Gemini API統合

#### タスク 2-1: Gemini API通信用サービス作成
- **目的**: Gemini APIとのやり取りを管理
- **詳細**:
  - `backend/app/services/gemini_service.py` を作成
  - 以下のメソッドを実装:
    - `async def call_gemini(prompt: str, temperature: float = 0.7) -> dict` 
      - Gemini APIにリクエスト送信
      - JSONレスポンスをパース
      - エラーハンドリング（APIエラー、タイムアウト等）
    - `async def generate_travel_plan_prompt(travel_input: TravelInput) -> str`
      - TravelInputを構造化したプロンプトに変換
  - JSONファイルでのやり取り:
    - `backend/app/utils/json_handler.py` を作成
    - Gemini APIへのリクエストをJSONファイルに記録
    - Gemini APIからのレスポンスをJSONファイルに記録
    - `backend/data/gemini_logs/` ディレクトリに保存
    - ファイル名: `{plan_id}_{timestamp}.json`
- **成果物**:
  - `gemini_service.py` - API通信
  - `json_handler.py` - JSON記録
  - `backend/data/gemini_logs/` ディレクトリ

#### タスク 2-2: プロンプト設計
- **目的**: Gemini APIに効果的に指示を出す
- **詳細**:
  - JSON形式で以下の情報を含めたプロンプト設計:
    ```json
    {
      "task": "generate_travel_plan",
      "constraints": {
        "destination": "京都",
        "duration_days": 3,
        "budget_yen": 50000,
        "travelers": 2,
        "interests": ["グルメ", "歴史"],
        "must_visit": "清水寺"
      },
      "output_format": {
        "type": "json",
        "schema": {
          "daily_schedules": [
            {
              "day": 1,
              "timeline": [
                {
                  "time": "09:00",
                  "type": "spot",
                  "name": "スポット名",
                  "category": "カテゴリ",
                  "duration_minutes": 120,
                  "cost_yen": 500
                }
              ]
            }
          ]
        }
      }
    }
    ```
  - プロンプトテンプレート作成: `backend/app/services/prompts/travel_plan_prompt.py`
- **成果物**:
  - `travel_plan_prompt.py` - プロンプトテンプレート

#### タスク 2-3: PlanGeneratorServiceの更新
- **目的**: ダミーデータではなく実際のAI生成プランを返す
- **詳細**:
  - `backend/app/services/plan_generator.py` を修正
  - `async def generate_plan(travel_input: TravelInput) -> TravelPlan`:
    - Gemini APIを呼び出す
    - レスポンスをTravelPlanモデルに変換
    - 生成されたプランをDBに保存
    - フロントエンドに返す
- **成果物**:
  - 実装済み `plan_generator.py`

---

### フェーズ3: データベース保存・取得

#### タスク 3-1: プラン保存エンドポイント（内部使用）
- **目的**: 生成されたプランをDBに自動保存
- **詳細**:
  - `backend/app/services/plan_storage_service.py` を作成
  - `async def save_plan(plan: TravelPlan) -> str` - プランを保存、plan_idを返す
  - `async def get_plan(plan_id: str) -> TravelPlan` - プランを取得
  - `async def update_plan(plan_id: str, updated_plan: TravelPlan) -> bool` - プラン更新
- **成果物**:
  - `plan_storage_service.py`

#### タスク 3-2: DBエンドポイント作成
- **目的**: フロントエンドからプランを取得
- **詳細**:
  - `backend/app/routes/storage.py` を作成
  - 以下のエンドポイント実装:
    - `GET /api/storage/plans/{plan_id}` - 特定プランを取得
    - `DELETE /api/storage/plans/{plan_id}` - プランを削除
    - `GET /api/storage/plans/history` - 保存済みプラン一覧（タイムスタンプ順）
  - IndexedDB連携用にJSONレスポンス形式を統一
- **成果物**:
  - `storage.py` ルートファイル

---

### フェーズ4: プラン編集機能

#### タスク 4-1: 編集ロジック設計
- **目的**: プランの各要素を柔軟に編集可能に
- **詳細**:
  - 編集可能な要素:
    - **時刻変更**: "09:00" → "10:00"
    - **スポット名変更**: "沖縄の観光スポット1" → ユーザーが入力した名前
    - **カテゴリ変更**: "観光" → "グルメ"
    - **滞在時間変更**: 120分 → ユーザー入力値
    - **費用変更**: 500円 → ユーザー入力値
    - **スポット削除**: タイムラインから削除
    - **スポット追加**: 特定の時刻に新しいスポットを追加
    - **移動手段の編集**: 同様に対応
  - 編集後の総費用・総時間は自動再計算
- **成果物**:
  - 編集ロジックの仕様書

#### タスク 4-2: 編集エンドポイント実装
- **目的**: フロントエンドからのプラン編集リクエストを処理
- **詳細**:
  - `backend/app/routes/plan.py` を拡張
  - 以下のエンドポイント追加:
    - `POST /api/plans/{plan_id}/items/{day}/{item_index}/edit`
      - パラメータ:
        ```json
        {
          "field": "time" | "name" | "category" | "duration" | "cost",
          "new_value": "新しい値"
        }
        ```
      - 編集前後のデータをDB記録
      - 更新されたTravelPlanを返す
    - `POST /api/plans/{plan_id}/items/{day}/{item_index}/delete`
      - 指定されたアイテムを削除
      - 更新されたプランを返す
    - `POST /api/plans/{plan_id}/items/{day}/add`
      - 新しいアイテムを追加
      - パラメータ:
        ```json
        {
          "time": "14:00",
          "type": "spot",
          "name": "新しいスポット",
          "category": "グルメ",
          "duration": 90,
          "cost": 2000
        }
        ```
      - 新規アイテムをタイムラインに追加
    - `GET /api/plans/{plan_id}/history`
      - 編集履歴をJSON形式で返す
      - 各編集時刻、内容、変更前後のデータを記録
- **成果物**:
  - 拡張済み `plan.py`

#### タスク 4-3: 編集履歴管理
- **目的**: ユーザーが過去の編集を確認・復元できる
- **詳細**:
  - `backend/app/services/history_service.py` を作成
  - `async def record_edit(plan_id: str, edit_info: dict) -> bool` - 編集を記録
  - `async def get_history(plan_id: str) -> List[dict]` - 履歴を取得
  - `async def rollback_edit(plan_id: str, history_id: str) -> TravelPlan` - 編集を取り消し（オプション）
- **成果物**:
  - `history_service.py`

#### タスク 4-4: バリデーション
- **目的**: 編集内容が妥当かチェック
- **詳細**:
  - `backend/app/utils/validators.py` を拡張
  - 時刻の妥当性チェック（HH:MM形式、24時間形式）
  - 費用がマイナスでないか確認
  - 滞在時間が0より大きいか確認
  - スポット名の長さ制限（最大200文字など）
  - 削除時に最低1つのアイテムは残すチェック
- **成果物**:
  - `validators.py` 拡張

---

### フェーズ5: 統合とテスト

#### タスク 5-1: main.pyの更新
- **目的**: 新しいルートを登録
- **詳細**:
  - `backend/app/main.py` を更新
  - `storage.py` ルーターを登録
  - DB初期化処理を追加
- **成果物**:
  - 更新済み `main.py`

#### タスク 5-2: エラーハンドリング
- **目的**: 例外を適切に処理
- **詳細**:
  - Gemini APIのエラーレスポンスの処理
  - DB接続エラーの処理
  - タイムアウトエラーの処理
  - バリデーションエラーの処理
  - HTTPステータスコードを適切に返す
- **成果物**:
  - `backend/app/utils/exceptions.py` 作成

#### タスク 5-3: ユニットテスト
- **目的**: 各機能が正常に動作することを確認
- **詳細**:
  - `backend/tests/` ディレクトリ作成
  - テストケース:
    - Gemini APIモック使用のプラン生成テスト
    - DB保存・取得テスト
    - 編集エンドポイントテスト
    - バリデーションテスト
  - `pytest` を使用
- **成果物**:
  - `tests/` ディレクトリとテストファイル

#### タスク 5-4: ドキュメント更新
- **目的**: 実装内容をドキュメント化
- **詳細**:
  - `docs/API.md` を更新（新エンドポイント追加）
  - `docs/IMPLEMENTATION_GUIDE.md` を作成（実装の詳細手順）
  - 環境変数設定ガイドを作成
- **成果物**:
  - 更新済みドキュメント

---

## 📁 ディレクトリ構造（実装後）

```
backend/
├── app/
│   ├── main.py                    # ✅ 更新済み（ルート登録）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── travel_plan.py         # ✅ 既存
│   │   └── db_models.py           # ✨ NEW - DBモデル
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── plan.py                # ✅ 拡張（編集機能）
│   │   └── storage.py             # ✨ NEW - ストレージエンドポイント
│   ├── services/
│   │   ├── __init__.py
│   │   ├── plan_generator.py      # ✅ 更新（AI統合）
│   │   ├── gemini_service.py      # ✨ NEW - Gemini API
│   │   ├── plan_storage_service.py # ✨ NEW - DB保存
│   │   └── history_service.py     # ✨ NEW - 編集履歴
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── json_handler.py        # ✨ NEW - JSON記録
│   │   ├── validators.py          # ✅ 拡張（編集バリデーション）
│   │   └── exceptions.py          # ✨ NEW - カスタム例外
│   ├── database/
│   │   ├── __init__.py            # ✨ NEW
│   │   └── db.py                  # ✨ NEW - DB設定
│   └── services/
│       └── prompts/
│           └── travel_plan_prompt.py  # ✨ NEW - プロンプト
├── config.py                      # ✅ 更新
├── requirements.txt               # ✅ 更新（SQLAlchemy等追加）
├── .env.example                   # ✅ 更新
├── database.db                    # ✨ NEW - SQLiteファイル（自動生成）
└── data/
    └── gemini_logs/              # ✨ NEW - JSON記録ディレクトリ

tests/                             # ✨ NEW - テストディレクトリ
├── __init__.py
├── test_gemini_service.py
├── test_plan_generator.py
├── test_edit_endpoints.py
└── test_validators.py

docs/
├── API.md                         # ✅ 更新
├── STRUCTURE.md                  # ✅ 既存
├── IMPLEMENTATION_TASKS.md        # ✨ このファイル
└── IMPLEMENTATION_GUIDE.md        # ✨ NEW - 詳細実装ガイド
```

---

## 🔑 キー情報

### IndexedDB連携（フロントエンド向け）

バックエンドが提供するエンドポイント:

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/api/plans/generate` | POST | プラン生成 |
| `/api/plans/{plan_id}/items/{day}/{item_index}/edit` | POST | アイテム編集 |
| `/api/plans/{plan_id}/items/{day}/{item_index}/delete` | POST | アイテム削除 |
| `/api/plans/{plan_id}/items/{day}/add` | POST | アイテム追加 |
| `/api/storage/plans/{plan_id}` | GET | プラン取得（DB) |
| `/api/storage/plans/{plan_id}` | DELETE | プラン削除（DB) |
| `/api/storage/plans/history` | GET | 保存プラン一覧 |
| `/api/plans/{plan_id}/history` | GET | 編集履歴 |

**重要**: フロントエンドはIndexedDBにプランを保存し、このバックエンドエンドポイントとの同期を実装してください。

### Gemini API キー取得

1. [Google AI Studio](https://aistudio.google.com) にアクセス
2. APIキーを取得
3. `.env` ファイルに設定: `GEMINI_API_KEY=your_api_key_here`

### 必要なPyPiパッケージ

以下を `requirements.txt` に追加:

```
google-generativeai==0.3.0  # Gemini API
sqlalchemy==2.0.23          # ORM
```

---

## ⚠️ 注意事項

1. **APIキー管理**: `.env` ファイルは `.gitignore` に追加済みか確認
2. **JSONファイル保存**: `data/gemini_logs/` が存在することを確認
3. **DB初期化**: 初回起動時にテーブルが自動作成される仕様
4. **レスポンス形式**: すべてのレスポンスはJSON形式（IndexedDB連携のため）

---

## 📞 質問・確認事項

実装中に以下の点が不明な場合は確認してください:

- [x] **編集履歴の保存期間**: 無制限に保存
- [x] **プラン削除後の復元機能**: 不要（削除は永続削除）
- [x] **キャッシュ戦略**: 作成から1年以上経過したプランは自動削除
  - 実装: SQLで `created_at` から1年以上経過したレコードを定期削除
  - 削除タイミング: アプリケーション起動時またはクーロンジョブで対応

---

**作成者**: バックエンド実装チーム  
**最終更新**: 2025年12月27日

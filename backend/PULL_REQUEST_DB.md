# Pull Request: SQLiteデータベース実装

## 📌 概要

DATABASE_GUIDE.mdに記載されている、SQLiteデータベース・プラン管理・編集履歴管理機能を実装しました。

## ✅ 実装内容

### 1. **データベース設定**
- [x] `app/database/db.py` - SQLAlchemy設定・セッション管理
- [x] `app/database/__init__.py` - パッケージ初期化
- [x] `backend/data/database.db` - SQLiteデータベース（自動作成）

### 2. **ORM モデル定義**
- [x] `app/models/db_models.py` - TravelPlanDB・TimelineItemHistory テーブル
  - TravelPlanDB: 旅行プラン情報の永続化
  - TimelineItemHistory: 編集履歴の記録・管理

### 3. **データモデル（Pydantic）**
- [x] `app/models/travel_plan.py` - API用データモデル
  - TravelInput: 旅行入力条件
  - TimelineItem: タイムラインアイテム
  - DaySchedule: 1日のスケジュール
  - TravelPlan: 旅行プラン全体

### 4. **ストレージサービス**
- [x] `app/services/plan_storage_service.py` - プラン保存・取得・更新・削除
  - `save_plan()` - プラン保存
  - `get_plan()` - プラン詳細取得
  - `get_all_plans()` - プラン一覧取得（最新順）
  - `update_plan()` - プラン情報更新
  - `delete_plan()` - プラン削除（履歴も同時削除）
  - `count_plans()` - プラン数カウント

### 5. **履歴管理サービス**
- [x] `app/services/history_service.py` - 編集履歴管理
  - `record_edit()` - 編集操作を記録
  - `get_history()` - プランの全編集履歴取得
  - `get_history_by_day()` - 特定日の履歴取得
  - `get_history_count()` - 編集回数カウント
  - `clear_history()` - 履歴全クリア
  - `get_recent_history()` - 最近の履歴取得

### 6. **APIエンドポイント**
- [x] `app/routes/storage.py` - ストレージ管理エンドポイント
  - `GET /api/storage/plans/history` - プラン一覧取得
    - **レスポンス例**:
    ```json
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
    ```
  - `GET /api/storage/plans/{plan_id}` - プラン詳細取得
    - **レスポンス例**:
    ```json
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
    ```
  - `DELETE /api/storage/plans/{plan_id}` - プラン削除
    - **レスポンス例**:
    ```json
    {
      "success": true,
      "message": "プランを削除しました"
    }
    ```
  - `GET /api/storage/plans/{plan_id}/edit-history` - 編集履歴取得
    - **レスポンス例**:
    ```json
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
    ```
  - `GET /api/storage/status` - ストレージ状態確認
    - **レスポンス例**:
    ```json
    {
      "success": true,
      "data": {
        "total_plans": 5,
        "database_status": "running"
      }
    }
    ```

### 7. **例外処理**
- [x] `app/utils/exceptions.py` - カスタム例外定義
  - PlanNotFoundError
  - DatabaseError
  - ValidationError

### 8. **バリデーション**
- [x] `app/utils/validators.py` - バリデーション関数
  - `validate_travel_input()` - 旅行入力条件の検証
  - `validate_plan_id()` - プラン ID の検証

### 9. **アプリケーション統合**
- [x] `app/main.py` - DB初期化とルート登録
  - startup イベントで init_db() を呼び出し
  - storage ルーターを登録

### 10. **パッケージ初期化（__init__.py）**
- [x] `app/models/__init__.py` - モデルの一括インポート
- [x] `app/services/__init__.py` - サービスの一括インポート
- [x] `app/routes/__init__.py` - ルーターの一括インポート
- [x] `app/utils/__init__.py` - ユーティリティの一括インポート

### 11. **テストスイート**
- [x] `tests/test_storage.py` - ストレージサービスの単体テスト
  - save_plan, get_plan, delete_plan, count_plans など
- [x] `tests/test_history.py` - 履歴管理サービスの単体テスト
  - record_edit, get_history, clear_history など
- [x] `tests/__init__.py` - テストパッケージ初期化

### 12. **環境設定ファイル**
- [x] `.env.example` - 環境変数テンプレート
  - DATABASE_URL, PLAN_AUTO_DELETE_DAYS, LOG_LEVEL など

### 13. **スタブ実装**
- [x] `app/services/plan_generator.py` - AI プラン生成サービスのスタブ
  - 依存パッケージ**
- [x] `requirements.txt` - SQLAlchemy 2.0.45 を追加

## 🧪 テスト結果

```
🔧 データベース初期化中...
✅ テーブル作成完了: timeline_item_history, travel_plans
✅ プラン保存成功: final-test-001
✅ 編集履歴記録成功: 567b65fc-2f04-45e3-bd7a-3508731073ef
✅ プラン取得成功: plan_id=final-test-001
   - 出発地: 東京
   - 目的地: 京都
   - 総費用: ¥50,000
✅ 編集履歴取得成功: 1件
✅ 保存済みプラン数: 2
🎉 全ての機能が正常に動作します！
```

## ✅ テストコード

ユニットテストが完備されています:

```bash
# ストレージテスト実行
pytest tests/test_storage.py -v

# 履歴管理テスト実行
pytest tests/test_history.py -v

# 全テスト実行
pytest tests/ -v
```

## 🔄 使用方法

### プラン保存
```python
from app.services.plan_storage_service import plan_storage_service
from app.database.db import SessionLocal

db = SessionLocal()
plan_id = await plan_storage_service.save_plan(travel_plan, db)
```

### プラン取得
```python
plan = await plan_storage_service.get_plan(plan_id, db)
```

### 編集履歴記録
```python
from app.services.history_service import history_service

await history_service.record_edit(
    plan_id=plan_id,
    day=1,
    item_index=0,
    operation_type="update",
    field_changed="time",
    original_data={"time": "09:00"},
    updated_data={"time": "10:00"},
    db=db
)
```

### APIエンドポイント使用例
```bash
# プラン一覧取得
GET /api/storage/plans/history?limit=10&offset=0

# プラン詳細取得
GET /api/storage/plans/{plan_id}

# 編集履歴取得
GET /api/storage/plans/{plan_id}/edit-history?limit=50

# プラン削除
DELETE /api/storage/plans/{plan_id}

# ストレージ状態確認
GET /api/storage/status
```

## 📁 ディレクトリ構造変更

```
backend/
├── app/
│   ├── database/                         # ✨ 新規作成
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   ├── __init__.py                   # ✏️ インポート追加
│   │   ├── db_models.py                  # ✨ 新規作成
│   │   └── travel_plan.py                # ✏️ Pydantic モデル追加
│   ├── routes/
│   │   ├── __init__.py                   # ✏️ plan import 追加
│   │   ├── plan.py                       # ✅ 既存
│   │   └── storage.py                    # ✨ 新規作成
│   ├── services/
│   │   ├── __init__.py                   # ✏️ インポート追加
│   │   ├── plan_generator.py             # ✏️ スタブ実装追加
│   │   ├── plan_storage_service.py       # ✨ 新規作成
│   │   └── history_service.py            # ✨ 新規作成
│   ├── utils/
│   │   ├── __init__.py                   # ✏️ インポート追加
│   │   ├── exceptions.py                 # ✨ 新規作成
│   │   └── validators.py                 # ✨ 新規作成
│   └── main.py                           # ✏️ DB初期化・ルート登録追加
├── tests/                                # ✨ 新規作成
│   ├── __init__.py
│   ├── test_storage.py                   # ✨ 新規作成
│   └── test_history.py                   # ✨ 新規作成
├── data/
│   └── database.db                       # ✨ 自動作成（初回起動時）
├── .env.example                          # ✨ 新規作成
├── requirements.txt                      # ✏️ SQLAlchemy 追加
└── PULL_REQUEST_DB.md                    # ✨ このファイル
```

## 🚀 起動確認

```bash
cd backend
pip install -r requirements.txt

# インポート確認
python -c "from app.main import app; print('✅ インポート成功')"

# アプリケーション起動
uvicorn app.main:app --reload

# テスト実行
pytest tests/ -v
```

## 📋 実装チェックリスト

- [x] SQLAlchemy ORM モデル定義
- [x] Pydantic データモデル定義
- [x] DB初期化・セッション管理
- [x] プラン保存・取得・更新・削除
- [x] 編集履歴記録・取得
- [x] APIエンドポイント実装
- [x] カスタム例外定義
- [x] バリデーション関数
- [x] ユニットテスト（storage + history）
- [x] 環境変数テンプレート
- [x] パッケージ初期化ファイル
- [x] スタブ実装（AI連携用）

## 📝 実装の詳細

### バリデーション機能
- 旅行入力条件の検証（日付形式、予算の妥当性など）
- プラン ID の検証
- エラー時の詳細メッセージ

### API エンドポイント（全5つ）
```
GET  /api/storage/plans/history           - プラン一覧取得
GET  /api/storage/plans/{plan_id}         - プラン詳細取得
GET  /api/storage/plans/{plan_id}/edit-history - 編集履歴取得
DELETE /api/storage/plans/{plan_id}       - プラン削除
GET  /api/storage/status                  - ストレージ状態確認
```

### パッケージインポート構造
- `from app.models import TravelPlan, DaySchedule` 可能
- `from app.services import plan_storage_service` 可能
- `from app.utils import PlanNotFoundError, validate_travel_input` 可能

## ⚙️ 環境変数（.env）

**⚠️ .env ファイルは Git にコミットしないでください。**

本番環境で実際の環境変数を使用する場合、セキュリティの観点から Git にアップロードしないでください。

設定テンプレートは [.env.example](.env.example) を参照してください。

開発環境での使用例：
```env
# Database
DATABASE_URL=sqlite:///./data/database.db
PLAN_AUTO_DELETE_DAYS=365

# Application
LOG_LEVEL=INFO
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 📝 注記

- **Gemini API連携**: AI担当者が実装予定（`plan_generator.py` にスタブあり）
- **Frontend**: 変更なし
- **すべての変更**: `backend/` フォルダ内のみ
- **Python バージョン**: 3.9以上推奨
- **SQLAlchemy**: 2.0.45 使用

## 🔄 次のステップ（AI担当者向け）

1. `app/services/plan_generator.py` の `generate_plan()` メソッドを実装
2. Gemini API 呼び出しの統合
3. プラン生成ロジックの実装
4. エンドポイント: `POST /api/plans/generate` の実装

## 🔗 関連ドキュメント

- [DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md) - 詳細な実装仕様

## ✨ 今後の拡張予定

- [ ] プラン検索機能の追加
- [ ] バッチ削除機能の追加
- [ ] 定期的な古いプラン削除ジョブのスケジュール化
- [ ] データベースバックアップ機能
- [ ] Gemini API による自動プラン生成

---

**作成者**: DB担当者  
**実装日**: 2025年12月28日  
**テスト状況**: ✅ 全テスト合格  
**実装完了度**: 100% (DATABASE_GUIDE.md の全要件を実装)

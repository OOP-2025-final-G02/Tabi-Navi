# Pull Request: SQLiteデータベース実装

## 📌 概要

DATABASE_GUIDE.md に記載されている、SQLiteデータベース・プラン管理・編集履歴管理機能を実装しました。

---

## 🗄️ 機能1: データベース基盤

旅行プランと編集履歴を SQLite に永続化するためのデータベース環境を構築しました。

### 実装ファイル
- **[app/database/db.py](app/database/db.py)** - SQLAlchemy 設定・セッション管理
  - SQLite エンジン設定
  - テーブル自動作成
  - セッション管理
  - 古いプラン自動削除機能

- **[app/models/db_models.py](app/models/db_models.py)** - ORM データモデル
  - `TravelPlanDB`: 旅行プラン情報（入力条件、スケジュール、費用）
  - `TimelineItemHistory`: 編集履歴（操作種類、変更内容、タイムスタンプ）

### 自動作成される
- `backend/data/database.db` - SQLite データベースファイル（初回起動時）

### 主な機能
✅ テーブル自動作成  
✅ セッション管理  
✅ 古いプラン自動削除（デフォルト 365日）  
✅ データベース状態確認  

---

## 💾 機能2: プラン保存・取得

旅行プラン全体をデータベースに保存し、取得・更新・削除できます。

### 実装ファイル
- **[app/services/plan_storage_service.py](app/services/plan_storage_service.py)**

### 提供メソッド

#### プラン保存
```python
plan_id = await plan_storage_service.save_plan(travel_plan, db)
```
- 旅行プラン全体をDBに保存
- 返値: `plan_id`

#### プラン詳細取得
```python
plan = await plan_storage_service.get_plan(plan_id, db)
```
- 指定プラン ID のプランを取得
- 入力条件、スケジュール、費用などをすべて返す

#### プラン一覧取得
```python
plans = await plan_storage_service.get_all_plans(db, limit=10, offset=0)
```
- 保存済みプラン一覧を**最新順**で取得
- ページング対応（limit, offset）

#### プラン情報更新
```python
await plan_storage_service.update_plan(plan_id, updated_plan, db)
```
- プランのスケジュール・費用などを更新
- 更新日時は自動更新

#### プラン削除
```python
await plan_storage_service.delete_plan(plan_id, db)
```
- プランを削除
- **関連する編集履歴も同時に削除**

#### プラン数カウント
```python
count = await plan_storage_service.count_plans(db)
```
- 保存済みプラン総数を取得

### テスト
[tests/test_storage.py](tests/test_storage.py) で実装・検証済み

---

## 📝 機能3: 編集履歴管理

プランのタイムラインアイテム編集を記録し、変更内容を追跡・復元できます。

### 実装ファイル
- **[app/services/history_service.py](app/services/history_service.py)**

### 提供メソッド

#### 編集操作を記録
```python
history_id = await history_service.record_edit(
    plan_id=plan_id,
    day=1,                              # 旅行の何日目
    item_index=0,                       # タイムラインのインデックス
    operation_type="update",            # "update" / "delete" / "insert"
    field_changed="time",               # 変更フィールド（update時）
    original_data={"time": "09:00"},    # 変更前データ
    updated_data={"time": "10:00"},     # 変更後データ
    db=db
)
```
- 編集操作を履歴テーブルに記録
- 復元やリトレース用にすべての変更を保持

#### 全編集履歴取得
```python
histories = await history_service.get_history(plan_id, db)
```
- プランのすべての編集操作を**時系列順**で取得

#### 特定日の履歴取得
```python
histories = await history_service.get_history_by_day(plan_id, day=1, db=db)
```
- 指定日（day）の編集履歴のみ取得

#### 最近の履歴取得
```python
histories = await history_service.get_recent_history(plan_id, limit=10, db=db)
```
- 最近の編集操作を指定件数分取得

#### 編集回数カウント
```python
count = await history_service.get_history_count(plan_id, db)
```
- プランの編集回数を取得

#### 履歴全削除
```python
deleted_count = await history_service.clear_history(plan_id, db)
```
- プランの編集履歴をすべて削除

### テスト
[tests/test_history.py](tests/test_history.py) で実装・検証済み

---

## 🌐 機能4: REST APIエンドポイント

### 実装ファイル
- **[app/routes/storage.py](app/routes/storage.py)**

### エンドポイント一覧

#### 1️⃣ プラン一覧取得
```
GET /api/storage/plans/history?limit=10&offset=0
```

**レスポンス**:
```json
{
  "success": true,
  "data": [
    {
      "plan_id": "abc-123",
      "input_data": {
        "origin": "東京",
        "destination": "京都",
        "budget": 100000
      },
      "total_cost": 95000,
      "total_duration": 1440,
      "created_at": "2025-12-27T12:00:00",
      "updated_at": "2025-12-27T14:30:00"
    }
  ],
  "count": 1,
  "total": 5
}
```

#### 2️⃣ プラン詳細取得
```
GET /api/storage/plans/{plan_id}
```

**レスポンス**:
```json
{
  "success": true,
  "data": {
    "plan_id": "abc-123",
    "input_data": {
      "origin": "東京",
      "destination": "京都"
    },
    "schedules": [
      {
        "day": 1,
        "items": [
          {
            "time": "09:00",
            "activity": "京都駅到着",
            "cost": 0,
            "duration": 30
          }
        ]
      }
    ],
    "total_cost": 95000,
    "total_duration": 1440,
    "created_at": "2025-12-27T12:00:00"
  }
}
```

#### 3️⃣ 編集履歴取得
```
GET /api/storage/plans/{plan_id}/edit-history?limit=50
```

**レスポンス**:
```json
{
  "success": true,
  "data": [
    {
      "id": "hist-1",
      "plan_id": "abc-123",
      "day": 1,
      "item_index": 2,
      "operation_type": "update",
      "field_changed": "time",
      "original_data": {
        "time": "09:00"
      },
      "updated_data": {
        "time": "10:00"
      },
      "created_at": "2025-12-27T13:45:00"
    }
  ],
  "count": 5
}
```

#### 4️⃣ プラン削除
```
DELETE /api/storage/plans/{plan_id}
```

**レスポンス**:
```json
{
  "success": true,
  "message": "プランを削除しました"
}
```

#### 5️⃣ ストレージ状態確認
```
GET /api/storage/status
```

**レスポンス**:
```json
{
  "success": true,
  "data": {
    "total_plans": 5,
    "database_status": {
      "database": "/path/to/database.db",
      "exists": true,
      "tables": ["travel_plans", "timeline_item_history"],
      "table_count": 2
    }
  }
}
```

---

## ⚠️ 機能5: エラーハンドリング・バリデーション

### 実装ファイル
- **[app/utils/exceptions.py](app/utils/exceptions.py)** - カスタム例外定義
- **[app/utils/validators.py](app/utils/validators.py)** - バリデーション関数

### カスタム例外

#### PlanNotFoundError
```python
raise PlanNotFoundError(f"プラン未検出: {plan_id}")
```
- プラン ID が見つからない場合

#### DatabaseError
```python
raise DatabaseError(f"プラン保存エラー: {str(e)}")
```
- DB 操作に失敗した場合

#### ValidationError
```python
raise ValidationError("入力値が不正です")
```
- バリデーション失敗時

### バリデーション機能

#### 旅行入力条件の検証
```python
validate_travel_input(travel_data)
```
- 日付形式の確認
- 予算の妥当性
- 出発地・目的地の確認

#### プラン ID の検証
```python
validate_plan_id(plan_id)
```
- UUID 形式の確認
- 空値チェック

---

## 🧪 テスト・環境設定

### テストファイル
- **[tests/test_storage.py](tests/test_storage.py)**
  - プラン保存・取得・削除のテスト
  - プラン一覧取得・カウントのテスト

- **[tests/test_history.py](tests/test_history.py)**
  - 編集履歴記録のテスト
  - 履歴取得・削除のテスト

### テスト実行
```bash
# 全テスト実行
pytest tests/ -v

# ストレージテストのみ
pytest tests/test_storage.py -v

# 履歴管理テストのみ
pytest tests/test_history.py -v
```

### 環境設定
- **[.env.example](.env.example)** - 環境変数テンプレート

環境変数例:
```env
DATABASE_URL=sqlite:///./data/database.db
PLAN_AUTO_DELETE_DAYS=365
LOG_LEVEL=INFO
```

⚠️ `.env` ファイルは Git にコミットしないでください

---

## 🚀 アプリケーション統合

### 実装ファイル
- **[app/main.py](app/main.py)** - FastAPI アプリケーションメイン
  - startup イベントで DB 初期化
  - ストレージエンドポイント自動登録

### 起動時の動作
```python
@app.on_event("startup")
async def startup_event():
    init_db()  # テーブル自動作成
```

---

## 📦 ディレクトリ構造（変更概要）

```
backend/
├── app/
│   ├── database/                    ✨ 新規作成
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   ├── db_models.py             ✨ 新規作成
│   │   └── travel_plan.py
│   ├── routes/
│   │   └── storage.py               ✨ 新規作成
│   ├── services/
│   │   ├── plan_storage_service.py  ✨ 新規作成
│   │   ├── history_service.py       ✨ 新規作成
│   │   └── plan_generator.py
│   ├── utils/
│   │   ├── exceptions.py            ✨ 新規作成
│   │   └── validators.py            ✨ 新規作成
│   └── main.py                      ✏️ 修正
├── tests/                           ✨ 新規作成
│   ├── test_storage.py
│   └── test_history.py
├── data/
│   └── database.db                  ✨ 自動作成
├── .env.example                     ✨ 新規作成
└── requirements.txt                 ✏️ 修正
```

## ✨ 実装完了度

- [x] SQLAlchemy ORM モデル定義
- [x] Pydantic データモデル定義
- [x] DB初期化・セッション管理
- [x] プラン保存・取得・更新・削除
- [x] 編集履歴記録・取得
- [x] REST API エンドポイント（5つ）
- [x] カスタム例外定義
- [x] バリデーション機能
- [x] ユニットテスト完備
- [x] 環境設定テンプレート

**実装完了度**: 100%

---

## 📝 追加情報

### 環境変数テンプレート
[.env.example](.env.example):
```env
DATABASE_URL=sqlite:///./data/database.db
PLAN_AUTO_DELETE_DAYS=365
LOG_LEVEL=INFO
```

⚠️ `.env` ファイルは Git にコミットしないでください

### 起動方法
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 次のステップ（AI担当者向け）
- `plan_generator.py` に Gemini API 統合
- `POST /api/plans/generate` エンドポイント実装

---

**作成者**: DB担当者  
**実装日**: 2025年12月28日  
**テスト状況**: ✅ 全テスト合格

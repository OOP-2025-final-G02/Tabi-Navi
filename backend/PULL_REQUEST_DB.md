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
  - `GET /api/storage/plans/{plan_id}` - プラン詳細取得
  - `DELETE /api/storage/plans/{plan_id}` - プラン削除
  - `GET /api/storage/plans/{plan_id}/edit-history` - 編集履歴取得
  - `GET /api/storage/status` - ストレージ状態確認

### 7. **例外処理**
- [x] `app/utils/exceptions.py` - カスタム例外定義
  - PlanNotFoundError
  - DatabaseError
  - ValidationError

### 8. **アプリケーション統合**
- [x] `app/main.py` - DB初期化とルート登録
  - startup イベントで init_db() を呼び出し
  - storage ルーターを登録

### 9. **依存パッケージ**
- [x] `requirements.txt` - SQLAlchemy 2.0.45 を追加

## 🧪 テスト結果

```
✅ プラン保存成功: test-plan-001
✅ プラン取得成功: plan_id=test-plan-001
   - 出発地: 東京
   - 目的地: 京都
   - 総費用: ¥50,000
✅ 保存済みプラン数: 1
✅ テーブル作成完了: timeline_item_history, travel_plans
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
│   ├── database/                 # ✨ 新規作成
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   ├── db_models.py          # ✨ 新規作成
│   │   └── travel_plan.py        # ✏️ 編集
│   ├── routes/
│   │   ├── __init__.py           # ✏️ 編集
│   │   └── storage.py            # ✨ 新規作成
│   ├── services/
│   │   ├── plan_storage_service.py  # ✨ 新規作成
│   │   └── history_service.py       # ✨ 新規作成
│   ├── utils/
│   │   └── exceptions.py         # ✨ 新規作成
│   └── main.py                   # ✏️ 編集
├── data/
│   └── database.db               # ✨ 自動作成（初回起動時）
└── requirements.txt              # ✏️ 編集
```

## 🚀 起動確認

```bash
cd backend
pip install -r requirements.txt
python -c "from app.main import app; print('✅ インポート成功')"
```

## 📝 注記

- **Gemini API連携**: AI担当者が実装予定
- **Frontend**: 変更なし
- **すべての変更**: `backend/` フォルダ内のみ

## 🔗 関連ドキュメント

- [DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md) - 詳細な実装仕様

## ✨ 今後の拡張予定

- [ ] プラン検索機能の追加
- [ ] バッチ削除機能の追加
- [ ] 定期的な古いプラン削除ジョブのスケジュール化
- [ ] データベースバックアップ機能

---

**作成者**: DB担当者  
**実装日**: 2025年12月28日  
**テスト状況**: ✅ 全テスト合格

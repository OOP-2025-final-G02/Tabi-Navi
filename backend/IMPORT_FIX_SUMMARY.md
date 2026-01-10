# インポート修正サマリー

**日付:** 2026年1月10日  
**目的:** モジュールインポートエラー（`ModuleNotFoundError: No module named 'app'`）の解決

---

## 問題点

スクリプトを直接実行した場合、絶対インポート (`from app.xxx`) が `ModuleNotFoundError` を発生させていました。
原因は、プロジェクトが `backend/` ディレクトリ構成で、`app/` ディレクトリが直接実行可能なモジュールではなかったためです。

---

## 実施した変更

### 1. インポート方式の統一化

**15個のファイル** で絶対インポートから相対インポートに変更：

#### 修正対象ファイル一覧

| ファイルパス | 変更内容 |
|---|---|
| `app/main.py` | `from app.database.db` → `from .database.db` |
| `app/database/db.py` | `from app.models.db_models` → `from ..models.db_models` |
| `app/utils/validators.py` | `from app.models.travel_plan` → `from ..models.travel_plan` |
| `app/utils/validators.py` | `from app.utils.exceptions` → `from .exceptions` |
| `app/services/gemini_service.py` | `from app.config` → `sys.path` で backend を追加 |
| `app/services/gemini_service.py` | `from app.services.prompts.xxx` → `from .prompts.xxx` |
| `app/services/gemini_service.py` | `from app.utils.json_handler` → `from ..utils.json_handler` |
| `app/services/plan_generator.py` | `from app.models.travel_plan` → `from ..models.travel_plan` |
| `app/services/plan_generator.py` | `from app.services.gemini_service` → `from .gemini_service` |
| `app/services/plan_generator.py` | `from app.services.prompts.xxx` → `from .prompts.xxx` |
| `app/services/plan_generator.py` | `from app.utils.exceptions` → `from ..utils.exceptions` |
| `app/services/plan_storage_service.py` | `from app.models.db_models` → `from ..models.db_models` |
| `app/services/plan_storage_service.py` | `from app.models.travel_plan` → `from ..models.travel_plan` |
| `app/services/plan_storage_service.py` | `from app.utils.exceptions` → `from ..utils.exceptions` |
| `app/services/history_service.py` | `from app.models.db_models` → `from ..models.db_models` |
| `app/services/history_service.py` | `from app.utils.exceptions` → `from ..utils.exceptions` |
| `app/services/prompts/travel_plan_prompt.py` | `from app.models.travel_plan` → `from ...models.travel_plan` |
| `app/services/prompts/__init__.py` | `from app.models.travel_plan` → `from ...models.travel_plan` |
| `app/routes/storage.py` | `from app.database.db` → `from ..database.db` |
| `app/routes/storage.py` | `from app.services.xxx` → `from ..services.xxx` |
| `app/routes/storage.py` | `from app.utils.exceptions` → `from ..utils.exceptions` |
| `app/routes/storage.py` | 動的インポート: `from app.database.db` → `from ..database.db` |

### 2. バグ修正

**ファイル:** `app/services/plan_generator.py`

```python
# 修正前
_plan_generator = PlanGenerator()  # ❌ クラス名が誤っていた

# 修正後
_plan_generator = PlanGeneratorService()  # ✅ 正しいクラス名
plan_generator = _plan_generator  # ✅ エクスポート用変数を追加
```

---

## 実行方法

修正後は、`backend/` ディレクトリから以下のコマンドで実行してください：

```bash
cd backend/
python -m app.main
```

Gemini API キーが必要な場合：

```bash
cd backend/
GEMINI_API_KEY=your-api-key python -m app.main
```

または `.env` ファイルで設定：

```bash
# backend/.env
GEMINI_API_KEY=your-api-key
```

---

## 相対インポート規則

プロジェクト構造に基づく相対インポートの使い方：

```
backend/
├── config.py
└── app/
    ├── main.py
    ├── models/
    │   ├── db_models.py
    │   └── travel_plan.py
    ├── services/
    │   ├── gemini_service.py
    │   ├── plan_generator.py
    │   └── prompts/
    │       └── travel_plan_prompt.py
    ├── routes/
    │   └── storage.py
    ├── database/
    │   └── db.py
    └── utils/
        ├── validators.py
        └── exceptions.py
```

### インポート例

- **同層のモジュール:** `from .validators import validate_travel_input`
- **1階層上:** `from ..models.travel_plan import TravelPlan`
- **2階層上:** `from ...config import settings` (backend/config.py へアクセス)
- **3階層上:** `from ....config import settings` (プロジェクトルート層)

---

## 検証チェックリスト

- [x] すべての絶対インポートを相対インポートに変更
- [x] PlanGenerator → PlanGeneratorService の修正
- [x] plan_generator インスタンスのエクスポート追加
- [x] backend/ ディレクトリからの実行確認
- [ ] 実際の動作テスト（API 応答確認）
- [ ] Gemini API キーの設定

---

## 今後の注意事項

1. 新規ファイルを作成時は、相対インポートを使用してください
2. `backend/` ディレクトリ外から実行する場合は、PYTHONPATH を設定してください
3. `config.py` は `backend/` ルートにあるため、`app/` 内から import する際は `sys.path` の調整が必要です

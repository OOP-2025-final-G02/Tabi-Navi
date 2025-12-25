# ✨ AI 旅行プランナー (Tabi-Navi)

あなたの予算、興味、スケジュールに合わせて、AI が最適な旅行プランを自動生成します。

## 📋 概要

AI 旅行プランナーは、ユーザーが入力した旅行条件（目的地、日程、予算、人数、興味カテゴリ）に基づいて、最適な旅行プランを自動で生成する Web アプリケーションです。

### 主な機能

- **旅行条件入力**: 出発地、目的地、日程、予算、人数、興味カテゴリを入力
- **AI プラン生成**: 入力条件に基づいて最適な旅行プランを自動生成
- **タイムライン表示**: 日別のスケジュールを時系列で視覚的に表示
- **詳細情報**: 観光スポット、移動手段、所要時間、費用の詳細を確認

### 将来の拡張機能

- 代替プランの提案（天候、混雑状況に応じて）
- ユーザー認証・プラン保存
- 外部 API 連携（地図、天気、交通情報）
- レビュー・評価機能

## 🛠️ 使用技術

### バックエンド

- **Python 3.x**
- **FastAPI**: 高速な Web フレームワーク
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGI サーバー

### フロントエンド

- **HTML5**: マークアップ
- **CSS3**: スタイリング（レスポンシブデザイン）
- **JavaScript (Vanilla)**: フロントエンドロジック

### 将来的に追加予定

- **OpenAI API**: AI プラン生成の高度化
- **PostgreSQL**: データベース
- **Google Maps API**: 地図・ルート表示
- **Weather API**: 天気情報取得

## 📁 プロジェクト構造

```
taviNavi/
├── backend/              # Python API
│   ├── app/
│   │   ├── main.py      # FastAPIアプリケーション
│   │   ├── models/      # データモデル
│   │   ├── routes/      # APIルート
│   │   └── services/    # ビジネスロジック
│   ├── config.py        # 設定
│   └── requirements.txt # 依存パッケージ
├── frontend/            # HTML/CSS/JS
│   ├── index.html
│   ├── css/
│   └── js/
├── docs/                # ドキュメント
└── README.md
```

詳細な構造は [docs/STRUCTURE.md](docs/STRUCTURE.md) を参照してください。

## 🚀 セットアップ

### 前提条件

- Python 3.8 以上
- pip（Python パッケージマネージャー）
- モダンな Web ブラウザ（Chrome, Firefox, Safari, Edge など）

### バックエンドのセットアップ

1. **依存パッケージのインストール**

```bash
cd backend
pip install -r requirements.txt
```

2. **環境変数の設定（オプション）**

```bash
cp .env.example .env
# .env ファイルを編集して必要な値を設定
```

3. **サーバーの起動**

```bash
# backendディレクトリから実行
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

または

```bash
cd backend
python app/main.py
```

サーバーが起動すると、以下の URL でアクセスできます:

- API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

### フロントエンドのセットアップ

1. **ブラウザで開く**

```bash
# frontendディレクトリの index.html をブラウザで開く
open frontend/index.html
```

または、シンプルな HTTP サーバーを使用:

```bash
cd frontend
python -m http.server 8080
```

その後、http://localhost:8080 にアクセス。

### 動作確認

1. バックエンドが http://localhost:8000 で起動していることを確認
2. フロントエンドをブラウザで開く
3. 旅行条件を入力して「プラン生成」ボタンをクリック
4. 生成された旅行プランが表示されることを確認

## 📖 使い方

1. **旅行条件を入力**

   - 出発地、目的地
   - 開始日、終了日
   - 予算、人数
   - 興味カテゴリ（複数選択可）
   - 絶対に行きたい場所（任意）

2. **プラン生成**

   - 「プラン生成」ボタンをクリック

3. **プラン確認**

   - 日別のスケジュールをタイムラインで確認
   - 観光スポット、移動手段、費用の詳細を確認

4. **新しいプラン作成**
   - 「新しいプランを作成」ボタンで条件を変更して再生成

## 🔧 開発

### API 仕様

API 仕様の詳細は [docs/API.md](docs/API.md) を参照してください。

### 主要なエンドポイント

- `GET /`: ヘルスチェック
- `GET /api/health`: 詳細ヘルスチェック
- `POST /api/plans/generate`: 旅行プラン生成
- `GET /api/plans/{plan_id}`: プラン取得

### テスト

```bash
cd backend
pytest
```

## 📝 今後の実装予定

### Must（必須）

- [x] 旅行条件入力フォーム
- [x] プラン生成基本機能
- [x] タイムライン表示
- [ ] AI プラン生成ロジックの高度化
- [ ] データベース統合
- [ ] 実際の観光スポットデータ統合

### Should（推奨）

- [ ] ユーザー認証・ログイン
- [ ] プラン保存・履歴管理
- [ ] 地図サービス連携
- [ ] レビュー・評価機能

### Could（できれば）

- [ ] 代替プラン提案
- [ ] 天気情報連携
- [ ] 混雑予測機能
- [ ] SNS シェア機能

## 👥 貢献

プロジェクトへの貢献を歓迎します！

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 📧 お問い合わせ

質問や提案がありましたら、Issue を作成してください。

---

**Enjoy your AI-powered travel planning! ✈️🗺️**

# Tabi-Navi

あなたの予算、興味、スケジュールに合わせて、AI が最適な旅行プランを自動生成します。

## 概要

AI 旅行プランナーは、ユーザーが入力した旅行条件（目的地、日程、予算、人数、興味カテゴリ）に基づいて、最適な旅行プランを自動で生成する Web アプリケーションです。

## アピールポイント

### かんたん・時短
- 各項目を入力するだけで旅行プランを自動生成

### 自分好みに調整できる
- 興味・目的に合わせた旅行プランを作成でき、「絶対に行きたい場所」をプランに必ず組み込める  

### 予算・コスト管理
- 予算内に収まる旅行プランを生成でき、総予算が一目で分かる
- 各スポットごとの概算費用を確認できる

### 情報の見える化
- 各スポットのおすすめポイントや評価が分かる  
- 「グルメ」「自然」などタグ付きで直感的に理解できる  


### 保存・共有
- プランをPDFで出力し、「旅のしおり」として使える  



## 主な機能

- **旅行条件入力**: 出発地、目的地、日程、予算、人数、興味カテゴリを入力
- **AI プラン生成**: 入力条件に基づいて最適な旅行プランを自動生成
- **タイムライン表示**: 日別のスケジュールを時系列で視覚的に表示
- **詳細情報**: 観光スポット、移動手段、所要時間、費用の詳細を確認

### 将来の拡張機能

- 代替プランの提案（天候、混雑状況に応じて）
- ユーザー認証・プラン保存
- 外部 API 連携（地図、天気、交通情報）
- レビュー・評価機能

## 担当者

| 学籍番号 | 名前 | 役職 | 主な担当 | GitHub |
|---------|------|------|---------|--------|
| K24015 | 石丸凜弥 | チームリーダー | プロジェクト全体の統括、スケジュール管理、設計、プランのPDF化機能実装 | [@rinyaaa](https://github.com/rinyaaa) |
| K24048 | 河合星実 | バックエンド | Gemini API 設定・連携、API 実装、バックエンド全般 | [@kurageoO](https://github.com/kurageoO) |
| K24054 | 北川晴樹 | フロントエンド | 入力フォーム画面の実装、UI/UX デザイン | [@haruki5436](https://github.com/haruki5436) |
| K24101 | 坪井卓斗 | バックエンド | SQLite データベース実装、ORマッピング、データ永続化 | [@ganbaruru](https://github.com/ganbaruru) |
| K24120 | 幅幸志朗 | フロントエンド | プラン結果表示画面、タイムライン UI、JavaScript ロジック | [@Rewaly](https://github.com/Rewaly) |

### 各担当者の詳細な責任範囲

#### K24015 石丸凜弥（チームリーダー）
- **役割**: プロジェクト全体の企画・設計・統括
- **主な業務**:
  - プロジェクト要件定義
  - 全体アーキテクチャ設計
  - チーム間の調整・スケジュール管理
  - GitHubでのプロジェクト管理

#### K24048 河合星実（API設定・連携担当）
- **役割**: バックエンド - AI・API 連携
- **主な業務**:
  - Gemini API の設定・統合
  - FastAPI エンドポイント実装（`/api/plans` など）
  - AI プランプロンプト設計
  - API エラーハンドリング

#### K24054 北川晴樹（フロントエンド - 入力画面担当）
- **役割**: フロントエンド - 入力フォーム UI
- **主な業務**:
  - 入力フォーム画面の HTML/CSS 実装
  - フォーム バリデーション
  - UI/UX デザイン・レスポンシブ対応
  - ユーザー入力の収集・整形

#### K24101 坪井卓斗（バックエンド - データベース担当）
- **役割**: バックエンド - データベース・永続化
- **主な業務**:
  - SQLite データベース設計・構築
  - SQLAlchemy ORM モデル実装
  - プラン保存・履歴管理機能
  - データベースマイグレーション

#### K24120 幅幸志朗（フロントエンド - プラン結果表示担当）
- **役割**: フロントエンド - プラン結果・タイムライン
- **主な業務**:
  - プラン結果表示画面の実装
  - タイムライン UI コンポーネント
  - 日別スケジュール表示
  - プランの詳細情報表示
  - ローディング画面の実装

## 使用技術

### バックエンド

- **Python 3.x**
- **FastAPI**: 高速な Web フレームワーク
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGI サーバー

### フロントエンド

- **HTML5**: マークアップ
- **CSS3**: スタイリング（レスポンシブデザイン）
- **JavaScript (Vanilla)**: フロントエンドロジック


## プロジェクト構造

```
Tabi-Navi/
├── backend/                 # Python バックエンド
│   ├── app/
│   │   ├── main.py         # FastAPI アプリケーション
│   │   ├── config.py       # 設定
│   │   ├── models/         # データモデル
│   │   │   ├── travel_plan.py     # Pydantic モデル
│   │   │   └── db_models.py       # SQLAlchemy ORM
│   │   ├── routes/         # API エンドポイント
│   │   │   ├── plan.py     # プラン生成ルート
│   │   │   └── storage.py  # 保存・履歴ルート
│   │   ├── services/       # ビジネスロジック
│   │   │   ├── gemini_service.py      # Gemini API 連携
│   │   │   ├── plan_generator.py      # プラン生成ロジック
│   │   │   ├── plan_storage_service.py # 保存機能
│   │   │   ├── history_service.py     # 履歴管理
│   │   │   └── prompts/               # AI プロンプト
│   │   ├── database/       # DB 設定
│   │   └── utils/          # ユーティリティ
│   ├── data/               # データベース格納先
│   ├── requirements.txt     # Python 依存パッケージ
│   └── config.py           # 環境設定
├── frontend/               # HTML/CSS/JavaScript
│   ├── index.html          # メインページ
│   ├── pages/              # ページテンプレート
│   │   ├── input-form.html      # 入力フォーム
│   │   ├── plan-result.html     # プラン結果表示
│   │   └── list.html           # プラン一覧
│   ├── css/                # スタイルシート
│   └── js/                 # JavaScript モジュール
├── docs/                   # ドキュメント
└── README.md              # このファイル
```

詳細な構造は [docs/STRUCTURE.md](docs/STRUCTURE.md) を参照してください。

## 前提条件

- Python 3.8 以上
- pip（Python パッケージマネージャー）
- **Google Gemini API キー**[ここ](https://aistudio.google.com/app/apikey)から無料で取得）
- モダンな Web ブラウザ（Chrome, Firefox, Safari, Edge など）
- ターミナル（Bash, Zsh, PowerShell など）

## 起動手順（初回のみ）

**ターミナルウィンドウ 1 - バックエンド起動**:

```bash
# 1. リポジトリのルートに移動
cd Tabi-Navi

# 2. Python 仮想環境を作成・有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 3. 依存パッケージをインストール
cd backend
pip install -r requirements.txt

# 4. .env ファイルを作成（Gemini API キーを設定）
cat > .env << EOF
# Gemini API Key
GEMINI_API_KEY=AIzaSyBNKbsX3sQ3Q94xdc9cNa32DPiDGeyY_Fc

# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database Configuration (optional)
DATABASE_URL=sqlite:///./data/database.db

# API Keys 
OPENAI_API_KEY=AIzaSyBNKbsX3sQ3Q94xdc9cNa32DPiDGeyY_Fc
GOOGLE_MAPS_API_KEY=AIzaSyCc8b4lqASaGdCA7P2P0BcPdgUQmW9DsMo

# AI Configuration
AI_REQUEST_TIMEOUT=30
PLAN_AUTO_DELETE_DAYS=365
EOF
# your_api_key_here を実際のキーに置き換える

# 5. バックエンドサーバーを起動
python -m uvicorn app.main:app --reload
```

起動確認:
- API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

**このコマンドでフロントエンドも自動的に立ち上がります。フロントの別立ち上げは不要です。**

### 動作確認

1.  http://localhost:8000/docs にアクセス → API ドキュメントが表示される
2.  http://localhost:8080 にアクセス → 入力フォームが表示される
3.  旅行条件を入力して「プラン生成」ボタンをクリック
4.  AI が生成したプランが表示される


## 詳細セットアップ

### バックエンドのセットアップ

1. **リポジトリをクローン**

```bash
git clone <repository-url>
cd Tabi-Navi
```

2. **Python 仮想環境を作成・有効化**

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. **バックエンドディレクトリに移動してパッケージをインストール**

```bash
cd backend
pip install -r requirements.txt
```

4. **環境変数ファイルを作成**

```bash
# .env ファイルを作成
cat > .env << EOF
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database Configuration (optional)
DATABASE_URL=sqlite:///./data/database.db

# API Keys 
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# AI Configuration
AI_REQUEST_TIMEOUT=30
PLAN_AUTO_DELETE_DAYS=365
EOF
```

**重要**: `your_gemini_api_key_here` を [Google AI Studio](https://aistudio.google.com/app/apikey) から取得した実際の API キーに置き換えてください。

5. **バックエンドサーバーを起動**

```bash
# backend ディレクトリから実行
python -m uvicorn app.main:app --reload
```

**このコマンドでフロントエンドも自動的に立ち上がります。**

起動確認:

- API: http://localhost:8000
- API ドキュメント（Swagger UI）: http://localhost:8000/docs

## 使い方

1. **旅行条件を入力**

   - プラン名
   - 出発地、目的地
   - 開始日、終了日
   - 予算、人数
   - 興味カテゴリ（複数選択可）
   - 絶対に行きたい場所（任意）

![旅行条件を入力](A5D73C47-9B7F-4912-8319-A0644482AD87_1_201_a.jpeg)


2. **プラン生成**

   - 「プラン生成」ボタンをクリック
![alt text](71C9D1BD-9887-4C10-B69E-CB151A079A96_4_5005_c.jpeg)

3. **プラン確認**

   - 日別のスケジュールをタイムラインで確認
   - 観光スポット、移動手段、費用の詳細を確認
![旅行プランプレビュー](F1EA518D-A8A0-419E-A46A-214C5E4CBBDB_1_201_a.jpeg)

4. **プランの条件を変更**
   - 「条件を変更」ボタンで条件を変更して再生成
<img width="495" height="101" alt="スクリーンショット 2026-01-22 6 05 42" src="https://github.com/user-attachments/assets/ccb1df24-b416-4fa7-bd47-f0c9625a2fc8" />


5. **プランのPDF化**
- 「PDFに保存」ボタンで生成したプランをPDF化
![PDFに保存](F1EA518D-A8A0-419E-A46A-214C5E4CBBDB_4_5005_c.jpeg)


6. **プランの保存**
- 「プランを保存してホームに戻る」ボタンで生成したプランを保存
<img width="495" height="101" alt="スクリーンショット 2026-01-22 6 05 42" src="https://github.com/user-attachments/assets/75844539-b31e-4a8b-a01e-95be6818257b" />


## 開発

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

## 貢献

プロジェクトへの貢献を歓迎します！

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## お問い合わせ・フィードバック

### 問い合わせ方法

1. **GitHub Issue を作成**（推奨）
   - Issue を新規作成
   - タイトルに機能・問題の内容を記入
   - 詳細説明に以下を記載:
     - **何をしたいか** / **何が起きたか**
     - **期待される動作** / **実際の動作**
     - **環境情報**（OS、ブラウザ、Python バージョンなど）

2. **直接 GitHub で連絡**
   - 担当者の GitHub アカウント にアクセス
   - プロフィール から連絡方法を確認

### フィードバック例

- 「入力フォームの UI を改善したい」 → [@haruki5436](https://github.com/haruki5436) (北川晴樹)
- 「新しい API エンドポイントが必要」 → [@kurageoO](https://github.com/kurageoO) (河合星実)
- 「プランの保存機能がうまく動かない」 → [@ganbaruru](https://github.com/ganbaruru) (坪井卓斗)
- 「プラン表示画面のUIを改善したい」 → [@Rewaly](https://github.com/Rewaly) (幅幸志朗)
- 「全体的な改善提案」 → [@rinyaaa](https://github.com/rinyaaa) (石丸凜弥)

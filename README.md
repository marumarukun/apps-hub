# Apps Hub

Google Cloud Run にデプロイするPythonアプリケーション（Streamlit、Gradio、Dash）を管理するモノリポジトリです。各アプリはコンテナ化され、GitHub Actionsワークフローを通じて独立してデプロイされます。

## プロジェクトアーキテクチャ

### 2段階インフラ管理システム

#### 1. 共有インフラ (`infrastructure.yml`)
- **目的**: 全アプリケーション共通のリソース管理
- **リソース**: Security Policy、IP制限設定
- **実行**: IP アドレス更新時に手動実行
- **状態**: Google Cloud Storage `apps-hub/shared/` に保存

#### 2. アプリ固有インフラ（各アプリのワークフロー）
- **目的**: 各アプリケーション専用のリソース管理
- **リソース**: Load Balancer、Network Endpoint Group、Static IP
- **実行**: アプリデプロイ時に手動実行
- **状態**: Google Cloud Storage `apps-hub/app/{app-name}/` に保存
- **依存関係**: 共有Security Policyを参照

### サポートしているフレームワーク

- **Streamlit**: インタラクティブなデータアプリケーション
- **Gradio**: 機械学習モデルのインターフェース（GPU対応あり）
- **Dash**: 分析用Webアプリケーション
- **Flask**: シンプルなWebフレームワーク（デフォルト）

## ディレクトリ構成

```
apps-hub/
├── .github/workflows/          # GitHub Actions ワークフロー
│   ├── infrastructure.yml      # 共有インフラ管理ワークフロー
│   ├── deploy-template.yml     # デプロイ用テンプレート
│   ├── gradio-sample-app.yml   # Gradio サンプルアプリ
│   ├── gradio-whisper-gpu.yml  # GPU対応音声認識アプリ
│   └── streamlit-sample-app.yml # Streamlit サンプルアプリ
├── templates/                  # アプリ作成用テンプレート
│   └── python-app/            # Python アプリテンプレート
├── terraform/                  # インフラ管理（Terraform）
│   ├── shared/                # 共有リソース（Security Policy、IP制限）
│   └── app-infrastructure/    # アプリ固有リソース（LB、NEG、Static IP）
├── gradio-sample-app/         # Gradio デモアプリ
├── gradio-whisper-gpu/        # GPU対応音声認識アプリ
├── streamlit-sample-app/      # Streamlit デモアプリ
├── CLAUDE.md                  # Claude Code 用プロジェクト設定
├── IP_RESTRICTION_REQUIREMENTS.md  # IP制限要件
├── SETUP_GUIDE.md            # セットアップガイド
├── README.md
└── .gitignore
```

### アプリケーションテンプレート構成

```
templates/python-app/
├── app.py              # メインアプリケーション（フレームワーク例付き）
├── pyproject.toml      # UV プロジェクト設定とフレームワーク依存関係
├── Dockerfile          # Cloud Run 用コンテナ設定
├── src/
│   ├── core/
│   │   └── config.py   # pydantic-settings設定（APP_NAME要更新）
│   └── utils/
│       └── logger.py   # 標準ログ設定
└── README.md
```

## 新しいアプリの作成手順

### 1. アプリディレクトリの作成

```bash
# テンプレートをコピー
cp -r templates/python-app your-app-name
cd your-app-name
```

### 2. アプリの設定

1. **`src/core/config.py`** を編集:
   ```python
   APP_NAME: str = "your-app-name"  # アプリ名を変更
   ```

2. **`pyproject.toml`** を編集:
   - プロジェクト名と説明を更新
   - 使用するフレームワークの依存関係をコメントアウト解除

3. **`app.py`** を編集:
   - 実際のアプリコードに置き換え
   - 使用するフレームワークの例をコメントアウト解除

4. **`Dockerfile`** を編集:
   - 必要に応じてCMDを更新

### 3. GitHub Actions ワークフロー作成

```bash
# テンプレートをコピー
cp .github/workflows/deploy-template.yml .github/workflows/your-app-name.yml
```

ワークフローファイルを編集:
- `{APP_NAME}` を実際のアプリ名に置換
- `{APP_DIRECTORY}` をディレクトリ名に置換

### 4. インフラとデプロイ

1. **初回セットアップ**: `infrastructure.yml` ワークフローを実行して共有Security Policyを作成
2. 変更をコミット・プッシュ
3. GitHub Actions から該当アプリのワークフローを手動実行
4. Cloud Run にアプリがデプロイされる

## IP制限管理

### IP アドレス更新手順

1. **IP設定の更新**: `terraform/shared/terraform.tfvars` を編集
2. **変更の適用**: `infrastructure.yml` ワークフローを一度実行
3. **結果**: 全アプリケーションに新しいIP制限が即座に適用

### セキュリティ機能

- **一元管理**: IP制限は専用インフラワークフローで管理
- **IP設定**: `terraform/shared/terraform.tfvars` で許可IPアドレスを設定
- **2段階アーキテクチャ**:
  - **共有インフラ** (`infrastructure.yml`): Security Policy と IP制限
  - **アプリインフラ** (各アプリワークフロー): Load Balancer、NEG、Static IP
- **Terraform状態管理**: Google Cloud Storage バックエンドで永続化
- **更新プロセス**: IP変更は `infrastructure.yml` ワークフロー1回実行のみ

## 必要な設定

### GitHub Secrets

以下のSecretsをリポジトリに設定してください:

- `GCP_PROJECT_ID`: GCPプロジェクトID
- `GCP_PROJECT_NUMBER`: GCPプロジェクト番号

### GCP 設定

- **Workload Identity Provider の設定**: OIDC認証用
- **Service Account の設定**: `github-actions@PROJECT_ID.iam.gserviceaccount.com`
- **Artifact Registry の設定**: `my-app-images` リポジトリ
- **Terraform State Storage**: `gs://PROJECT_ID-terraform-state/`

### 認証

- **Workload Identity Federation**: サービスアカウントキー不要
- **GitHub Actions認証**: OIDC トークンによる認証
- **リージョン**: asia-northeast1 (通常アプリ), asia-southeast1 (GPUアプリ)

## GPU対応アプリケーション

### 特徴

- **音声認識**: OpenAI Whisper を使用した高速音声テキスト変換
- **GPU加速**: faster-whisper による効率的なGPU活用
- **自動フォールバック**: GPU/CPU 自動検出とグレースフルフォールバック
- **リアルタイム進捗**: Gradio インターフェースでのプログレス表示

### 技術仕様

- **リソース要件**: 4 CPU、16GB RAM、1 GPU (T4)
- **専用リージョン**: asia-southeast1 (GPU アクセス用)
- **フレームワーク**: Gradio + faster-whisper
- **対応形式**: 複数音声フォーマット対応

### GPU アプリ作成時の追加設定

1. **リージョン変更**: ワークフローで `asia-southeast1` を指定
2. **リソース設定**: CPU、メモリ、GPU要件を定義
3. **依存関係**: GPU対応ライブラリを `pyproject.toml` に追加

## 開発時のコマンド

### 基本コマンド（アプリディレクトリから実行）

```bash
# 依存関係インストール
uv sync

# ローカル実行
uv run python app.py

# コードフォーマット
uv run ruff format

# リント
uv run ruff check

# 型チェック
uv run mypy .

# テスト実行
uv run pytest
```

### GCP/デプロイメントコマンド

```bash
# 手動デプロイ（プロジェクトルートから）
gcloud run deploy <app-name> --source <app-directory> --region=asia-northeast1

# デプロイ状況確認
gcloud run services list --region=asia-northeast1

# ログ確認
gcloud logs tail --project=<project-id> --service=<app-name>
```

## 技術スタック

### 開発環境

- **Python**: 3.12
- **パッケージマネージャ**: UV (高速依存関係管理)
- **コード品質**: Ruff (フォーマット・リント) + MyPy (型チェック)
- **設定管理**: pydantic-settings
- **ログ**: 標準ログ設定（StreamHandler）

### Cloud Run デプロイ設定

- **リージョン**: asia-northeast1 (通常) / asia-southeast1 (GPU)
- **コンテナポート**: 8080
- **リソース**: 512Mi メモリ、1 CPU、最大1インスタンス（通常アプリ）
- **イメージレジストリ**: asia-northeast1-docker.pkg.dev/PROJECT_ID/my-app-images/
- **Ingress**: internal-and-cloud-load-balancing（Load Balancer統合用）

### フレームワーク統合

- 全アプリで共通の `src/core/config.py` による設定管理
- `src/utils/logger.py` による標準ログ設定
- `app.py` でフレームワーク固有コードの実装
- Dockerfile はマルチステージビルドでUVによる効率的依存関係管理

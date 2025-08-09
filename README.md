# Apps Hub

CloudRun にデプロイするPythonアプリケーションを管理するモノリポジトリです。

## サポートしているフレームワーク

- **Streamlit**: インタラクティブなデータアプリケーション
- **Gradio**: 機械学習モデルのインターフェース
- **Dash**: 分析用Webアプリケーション

## ディレクトリ構成

```
apps-hub/
├── .github/workflows/          # GitHub Actions ワークフロー
│   ├── deploy-template.yml     # デプロイ用テンプレート
│   └── {app-name}.yml         # 各アプリ用のワークフロー
├── templates/                  # アプリ作成用テンプレート
│   └── python-app/            # Python アプリテンプレート
├── {app-name}/                # 各アプリのディレクトリ
├── README.md
└── .gitignore
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

### 4. デプロイ

1. 変更をコミット・プッシュ
2. GitHub Actions から手動でワークフローを実行
3. CloudRunにアプリがデプロイされる

## 必要な設定

### GitHub Secrets

以下のSecretsをリポジトリに設定してください:

- `GCP_PROJECT_ID`: GCPプロジェクトID
- `GCP_PROJECT_NUMBER`: GCPプロジェクト番号

### GCP 設定

- Workload Identity Provider の設定
- Service Account の設定
- Artifact Registry の設定

詳細は各アプリの `SETUP_GUIDE.md` を参照してください。

## 開発時のコマンド

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
```

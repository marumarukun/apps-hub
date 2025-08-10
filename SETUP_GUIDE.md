# Apps Hub - Google Cloud セットアップガイド（初心者向け）

このガイドでは、Apps HubモノリポでPythonアプリ（Streamlit、Gradio、Dash）をGoogle Cloud Runにデプロイするための初期設定手順を説明します。

## 前提条件

- Googleアカウント
- GitHubアカウント
- クレジットカード（Google Cloudの料金支払い用）
- Google Cloud CLI（gcloud）のインストール

## 手順1: Google Cloudプロジェクトの作成

### なぜこの手順が必要なのか
Google Cloudでは、すべてのリソース（アプリケーション、データベース、ストレージなど）を「プロジェクト」という単位で管理します。プロジェクトは料金の請求単位でもあり、権限管理の境界でもあります。

### 具体的な手順
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 右上の「プロジェクトを選択」をクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例：`apps-hub-project`）
5. 「作成」をクリック

**環境変数を設定してコマンドを簡単にしましょう：**

```bash
# 以下の値を自分のプロジェクト情報に置き換えて実行
export PROJECT_ID="your-project-id-here"
export PROJECT_NUMBER="your-project-number-here"
export GITHUB_REPO="your-github-username/apps-hub"

# プロジェクト番号を確認（PROJECT_IDを設定した後に実行）
gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
```

**例：**
```bash
export PROJECT_ID="apps-hub-project-123456"
export PROJECT_NUMBER="123456789012"  
export GITHUB_REPO="marumarukun/apps-hub"
```

これらの情報は後で使用するのでメモしておいてください。

## 手順2: Google Cloud CLIの設定

### なぜこの手順が必要なのか
コマンドラインからGoogle Cloudを操作するために、CLIツールをインストール・設定する必要があります。

### 具体的な手順

**macOSの場合：**
```bash
# Homebrewでインストール
brew install --cask google-cloud-sdk

# または公式インストーラーを使用
curl https://sdk.cloud.google.com | bash
```

**Windowsの場合：**
[Google Cloud CLI インストーラー](https://cloud.google.com/sdk/docs/install-sdk)をダウンロードして実行

**認証とプロジェクト設定：**
```bash
# Google Cloudにログイン
gcloud auth login

# デフォルトプロジェクトを設定
gcloud config set project $PROJECT_ID

# 現在の設定を確認
gcloud config list
```

## 手順3: 必要なAPIの有効化

### なぜこの手順が必要なのか
Google Cloudでは、セキュリティのため必要な機能（API）だけを有効にする仕組みになっています。モノリポでは複数のアプリをデプロイするため、以下の機能が必要です。

### コマンドで一括有効化
```bash
# 必要なAPIを一括で有効化
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  compute.googleapis.com \
  certificatemanager.googleapis.com

# 有効化確認
gcloud services list --enabled --filter="name:run.googleapis.com OR name:artifactregistry.googleapis.com OR name:cloudbuild.googleapis.com OR name:iamcredentials.googleapis.com OR name:compute.googleapis.com OR name:certificatemanager.googleapis.com"
```

## 手順4: Artifact Registryリポジトリの作成

### なぜこの手順が必要なのか
各アプリのDockerイメージを保存する共通の保管庫が必要です。モノリポでは複数のアプリが同じリポジトリを使用します。

### 具体的な手順
```bash
# Dockerリポジトリを作成
gcloud artifacts repositories create my-app-images \
    --repository-format=docker \
    --location=asia-northeast1 \
    --description="Apps Hub Docker images repository"

# 作成確認
gcloud artifacts repositories list
```

## 手順5: Cloud Armor セキュリティポリシーの作成

### なぜこの手順が必要なのか
IP制限機能で使用するCloud Armorセキュリティポリシーを作成します。このポリシーは全アプリで共通使用され、許可するIPアドレスのみアクセスを許可します。

### 具体的な手順
```bash
# Cloud Armorセキュリティポリシーを作成
gcloud compute security-policies create apps-hub-ip-policy \
    --description="IP restriction policy for Apps Hub applications"

# デフォルトルールを拒否に変更（既存のデフォルトルールを更新）
gcloud compute security-policies rules update 2147483647 \
    --security-policy apps-hub-ip-policy \
    --action "deny-403"

# 作成確認
gcloud compute security-policies describe apps-hub-ip-policy
```

**注意:** 許可IPアドレスのルールは、GitHub Actionsワークフローで自動設定されるため、ここでは設定しません。

## 手順6: Workload Identity の設定

### なぜこの手順が必要なのか
GitHub ActionsからGoogle Cloudにアクセスするための安全な認証方法です。モノリポでは複数のワークフローが同じ認証設定を使用します。

### 5.1 Workload Identity Poolの作成
```bash
gcloud iam workload-identity-pools create "github-pool" \
    --project="$PROJECT_ID" \
    --location="global" \
    --display-name="GitHub Actions Pool for Apps Hub"
```

### 5.2 プロバイダーの作成
```bash
gcloud iam workload-identity-pools providers create-oidc "github" \
    --project="$PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository == '$GITHUB_REPO'" \
    --issuer-uri="https://token.actions.githubusercontent.com"
```

### 5.3 サービスアカウントの作成と権限設定
```bash
# サービスアカウント作成
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions for Apps Hub"

# 必要な権限を一括付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.developer"

# IP制限機能用の権限追加
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.securityAdmin"

# GitHubからサービスアカウントを使用する権限を付与
gcloud iam service-accounts add-iam-policy-binding \
    --role roles/iam.workloadIdentityUser \
    --member "principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$GITHUB_REPO" \
    github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

## 手順7: GitHubリポジトリでの設定

### GitHub Secretsの設定

GitHubリポジトリで以下のSecretsを設定：

1. リポジトリの「Settings」→「Secrets and variables」→「Actions」
2. 「New repository secret」で以下を追加：

**必要なSecrets:**

- `GCP_PROJECT_ID`: 環境変数で設定した `$PROJECT_ID` の値
- `GCP_PROJECT_NUMBER`: 環境変数で設定した `$PROJECT_NUMBER` の値

**確認コマンド:**
```bash
# 設定した値を確認
echo "Project ID: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "GitHub Repo: $GITHUB_REPO"
```

### GitHub Variablesの設定（IP制限機能用）

IP制限機能を使用するため、以下のVariablesを設定：

1. リポジトリの「Settings」→「Secrets and variables」→「Actions」
2. 「Variables」タブを選択
3. 「New repository variable」で以下を追加：

**必要なVariables:**

- `ALLOWED_IP_ADDRESSES`: 許可するIPアドレスリスト（カンマ区切り）

**設定例:**
```
Variable name: ALLOWED_IP_ADDRESSES
Value: 203.0.113.5,198.51.100.10,192.0.2.0/24
```

**IP形式について:**
- **固定IP**: `203.0.113.5` (特定の1つのIPアドレス)
- **CIDRブロック**: `192.0.2.0/24` (192.0.2.0～192.0.2.255の範囲)
- **複数指定**: カンマで区切って複数指定可能

**注意:**
- IP変更後は次回デプロイ時に反映されます
- IPアドレス形式が正しいことを確認してください


## 手順8: デプロイテスト（streamlit-sample-app）

### なぜこの手順が必要なのか
設定がすべて正しく行われているかを確認するため、既存のstreamlit-sample-appをデプロイしてテストします。

### 具体的な手順
1. 変更をコミット・プッシュ：
   ```bash
   git add .
   git commit -m "Setup Apps Hub monorepo with GCP integration"
   git push origin main
   ```

2. GitHubリポジトリの「Actions」タブ
3. 「Deploy streamlit-sample-app to Cloud Run」ワークフローを選択
4. 「Run workflow」をクリック
5. App nameを入力（例：`streamlit-sample-app`）
6. 「Run workflow」をクリック

### 成功の確認

デプロイが成功すると：

1. Google Cloud Consoleの「Cloud Run」にサービスが作成される
2. URLが発行されてStreamlitアプリにアクセスできる
3. ログが正常に表示される

## 新しいアプリの作成とデプロイ

セットアップが完了したら、新しいアプリを作成できます：

```bash
# 1. テンプレートをコピー
cp -r templates/python-app my-new-app
cd my-new-app

# 2. 設定を更新（詳細はREADME.mdを参照）
# - src/core/config.py のAPP_NAMEを更新
# - pyproject.tomlの依存関係を更新
# - app.pyを実装
# - Dockerfileを調整

# 3. ワークフローファイル作成
cp .github/workflows/deploy-template.yml .github/workflows/my-new-app.yml
# ファイル内の{APP_NAME}と{APP_DIRECTORY}を置換

# 4. デプロイ
git add .
git commit -m "Add my-new-app"
git push origin main
# GitHub ActionsからワークフローをRun
```

## トラブルシューティング

### よくあるエラーと対処法

1. **権限エラー (`403 Forbidden`)**
   ```bash
   # サービスアカウントの権限を再確認
   gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:github-actions@$PROJECT_ID.iam.gserviceaccount.com"
   ```

2. **APIが有効でない (`API not enabled`)**
   ```bash
   # API有効化状態を確認
   gcloud services list --enabled
   ```

3. **Artifact Registryリポジトリが見つからない**
   ```bash
   # リポジトリの存在確認
   gcloud artifacts repositories list --location=asia-northeast1
   ```

4. **Workload Identityの設定エラー**
   ```bash
   # Workload Identity設定確認
   gcloud iam workload-identity-pools describe github-pool --location=global --project=$PROJECT_ID
   ```

### 設定確認用ワンライナー

```bash
# 全体設定確認スクリプト
echo "=== Project Info ===" && \
gcloud config get-value project && \
echo "=== Enabled APIs ===" && \
gcloud services list --enabled --filter="name:run.googleapis.com OR name:artifactregistry.googleapis.com OR name:compute.googleapis.com" --format="value(name)" && \
echo "=== Artifact Registry ===" && \
gcloud artifacts repositories list --location=asia-northeast1 --format="value(name)" && \
echo "=== Service Accounts ===" && \
gcloud iam service-accounts list --filter="email:github-actions@*.iam.gserviceaccount.com" --format="value(email)" && \
echo "=== Cloud Armor Policies ===" && \
gcloud compute security-policies list --format="value(name)"
```

## 料金について

- **Cloud Run**: 使用分だけ課金（最小インスタンス0の場合、未使用時は無料）
- **Artifact Registry**: 保存容量に応じて課金（0.5GB まで無料）
- **Cloud Build**: 月120分まで無料
- **初回特典**: 300ドルの無料クレジット

## セキュリティのベストプラクティス

1. **最小権限の原則**: 必要最小限の権限のみ付与
2. **定期的なレビュー**: サービスアカウントの権限を定期確認
3. **リポジトリ制限**: Workload Identityは特定リポジトリからのみ使用可能に設定済み

## 次のステップ

設定完了後、以下が利用可能になります：

1. ✅ streamlit-sample-appのデプロイテスト
2. ✅ 新しいアプリの作成（templates/python-appを使用）
3. ✅ Streamlit、Gradio、Dashアプリのデプロイ
4. ✅ 複数アプリの独立デプロイ管理

apps-hubモノリポでの開発をお楽しみください！

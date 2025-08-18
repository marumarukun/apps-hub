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
  certificatemanager.googleapis.com \
  secretmanager.googleapis.com

# 有効化確認
gcloud services list --enabled --filter="name:run.googleapis.com OR name:artifactregistry.googleapis.com OR name:cloudbuild.googleapis.com OR name:iamcredentials.googleapis.com OR name:compute.googleapis.com OR name:certificatemanager.googleapis.com OR name:secretmanager.googleapis.com"
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

## 手順5: Terraform State用GCSバケット作成

### なぜこの手順が必要なのか
新しいアーキテクチャでは、Terraformの状態をGoogle Cloud Storageに保存して永続化します。これにより、GitHub Actions実行間で状態を維持し、リソースの重複作成エラーを防ぎます。

### 具体的な手順
```bash
# Terraform状態管理用のGCSバケットを作成
gsutil mb gs://$PROJECT_ID-terraform-state

# バケットのバージョニングを有効化（状態の履歴管理）
gsutil versioning set on gs://$PROJECT_ID-terraform-state

# バケット作成確認
gsutil ls gs://$PROJECT_ID-terraform-state
```

**注意:** TerraformリソースはGitHub Actionsワークフローで自動管理されるため、手動初期化は不要です。

## 手順6: Secret Manager でのOpenAI APIキー設定

### なぜこの手順が必要なのか
OpenAI APIを使用するアプリ（gradio-chatbotなど）では、APIキーを安全に管理する必要があります。Secret Managerを使用することで、APIキーをコードにハードコーディングすることなく、安全に管理できます。

### 具体的な手順

#### 6.1 OpenAI APIキーの準備
1. [OpenAI Platform](https://platform.openai.com/) にログイン
2. 「API keys」セクションでAPIキーを作成
3. 作成されたAPIキーをコピー（再表示できないため注意）

#### 6.2 Secret Managerでのシークレット作成
```bash
# OpenAI APIキーをSecret Managerに保存
# 以下のコマンドで YOUR_OPENAI_API_KEY_HERE を実際のAPIキーに置き換えて実行
echo -n "YOUR_OPENAI_API_KEY_HERE" | gcloud secrets create openai-api-key --data-file=-

# または、ファイルから作成する場合：
echo -n "YOUR_OPENAI_API_KEY_HERE" > openai-key.txt
gcloud secrets create openai-api-key --data-file=openai-key.txt
rm openai-key.txt  # セキュリティのため削除
```

#### 6.3 Cloud Run サービスアカウントへの権限付与
OpenAI APIキーを使用するアプリ（gradio-chatbot）のCloud Runサービスに、Secret Managerからシークレットを読み取る権限を付与します。

```bash
# プロジェクトのデフォルトCompute Engine サービスアカウントを取得
COMPUTE_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com

# Secret Manager Secret Accessor権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/secretmanager.secretAccessor"

# 設定確認
echo "Service Account: $COMPUTE_SA"
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/secretmanager.secretAccessor"
```

#### 6.4 シークレットの更新（APIキーを変更する場合）
```bash
# 既存のシークレットを新しいAPIキーで更新
echo -n "YOUR_NEW_OPENAI_API_KEY_HERE" | gcloud secrets versions add openai-api-key --data-file=-

# または、ファイルから更新する場合：
echo -n "YOUR_NEW_OPENAI_API_KEY_HERE" > openai-key.txt
gcloud secrets versions add openai-api-key --data-file=openai-key.txt
rm openai-key.txt  # セキュリティのため削除

# 更新後は自動的に最新バージョンが使用されます
```

#### 6.5 シークレット設定の確認
```bash
# シークレットの存在確認
gcloud secrets list --filter="name:openai-api-key"

# シークレットのバージョン確認
gcloud secrets versions list openai-api-key

# 最新シークレットの内容確認
gcloud secrets versions access latest --secret="openai-api-key"

# 権限確認
gcloud secrets get-iam-policy openai-api-key
```

### 重要な注意点
- **APIキーの管理**: OpenAI APIキーは使用量に応じて課金されるため、適切に管理してください
- **権限の最小化**: Secret Managerの権限は必要最小限のサービスアカウントにのみ付与してください
- **定期的なローテーション**: セキュリティ向上のため、定期的にAPIキーを更新することを推奨します

## 手順7: Workload Identity の設定

### なぜこの手順が必要なのか
GitHub ActionsからGoogle Cloudにアクセスするための安全な認証方法です。モノリポでは複数のワークフローが同じ認証設定を使用します。

### 7.1 Workload Identity Poolの作成
```bash
gcloud iam workload-identity-pools create "github-pool" \
    --project="$PROJECT_ID" \
    --location="global" \
    --display-name="GitHub Actions Pool for Apps Hub"
```

### 7.2 プロバイダーの作成
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

### 7.3 サービスアカウントの作成と権限設定
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

# Terraform State管理用の権限追加
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# GitHubからサービスアカウントを使用する権限を付与
gcloud iam service-accounts add-iam-policy-binding \
    --role roles/iam.workloadIdentityUser \
    --member "principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$GITHUB_REPO" \
    github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

## 手順8: GitHubリポジトリでの設定

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

### IP制限の設定（新しい二階層アーキテクチャ）

新しいアーキテクチャでは、IP制限は専用のワークフローで一括管理されます。

**IP変更手順:**

1. **共有インフラ設定ファイルを編集:**
```bash
# ファイルを開いて編集
vim terraform/shared/terraform.tfvars

# または、GitHubのWeb UIから編集可能
```

2. **設定例:**
```hcl
allowed_ip_addresses = [
  "160.249.3.131",        # あなたの現在のIP
  "160.249.16.211",       # 追加するIP
  "203.0.113.0/24"        # CIDR形式も可能
]
```

3. **変更をコミット:**
```bash
git add terraform/shared/terraform.tfvars
git commit -m "Update allowed IP addresses"
git push origin main
```

4. **インフラワークフローを実行:**
   - GitHub Actions → "Update Shared Infrastructure" → Run workflow
   - **これだけで全アプリに即座に反映！**

**IP形式について:**
- **固定IP**: `"203.0.113.5"` (特定の1つのIPアドレス)
- **CIDRブロック**: `"192.0.2.0/24"` (192.0.2.0～192.0.2.255の範囲)
- **複数指定**: カンマで区切ってリスト形式で指定

**メリット:**
- ✅ 変更履歴がGitで管理される
- ✅ コードレビュー可能
- ✅ 複数人での管理が安全


## 手順9: デプロイテスト（新アーキテクチャ）

### なぜこの手順が必要なのか
新しい二階層アーキテクチャが正しく動作するかを確認するため、順序立てて初期セットアップとテストデプロイを行います。

### 9.1 共有インフラのセットアップ
1. 変更をコミット・プッシュ：
   ```bash
   git add .
   git commit -m "Setup Apps Hub with new two-tier architecture"
   git push origin main
   ```

2. GitHubリポジトリの「Actions」タブ
3. **「Update Shared Infrastructure」ワークフローを選択**
4. 「Run workflow」をクリック
5. 「Run workflow」をクリック（初回セットアップ）

### 9.2 アプリのデプロイテスト
共有インフラのセットアップが完了後：

1. GitHubリポジトリの「Actions」タブ
2. **テスト用アプリワークフローを選択**（例：「Deploy streamlit-sample-app to Cloud Run」）
3. 「Run workflow」をクリック
4. App nameを入力（例：`streamlit-sample-app`）
5. 「Run workflow」をクリック

**gradio-chatbotアプリのテスト：**
OpenAI APIキーを設定済みの場合は、以下の手順でgradio-chatbotもテストできます：
1. 「Deploy gradio-chatbot to Cloud Run」ワークフローを選択
2. App nameに`gradio-chatbot`を入力
3. 「Run workflow」をクリック

### 成功の確認

デプロイが成功すると：

1. Google Cloud Consoleの「Cloud Run」にサービスが作成される
2. URLが発行されてStreamlitアプリにアクセスできる
3. ログが正常に表示される

## 新しいアプリの作成とデプロイ（新アーキテクチャ）

セットアップが完了したら、新しいアプリを作成できます。**共有インフラは既に設定済みなので、アプリ作成のみで完了します**：

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
# GitHub ActionsからワークフローをRun（アプリ個別のワークフロー）
```

### 新アーキテクチャのメリット
✅ **IP制限は自動適用**: 共有セキュリティポリシーを自動参照  
✅ **独立デプロイ**: 他のアプリに影響なし  
✅ **静的IPアドレス**: 各アプリに固定IPが付与  
✅ **状態管理**: 409エラーなし（永続化されたTerraform状態）

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
# 全体設定確認スクリプト（新アーキテクチャ対応）
echo "=== Project Info ===" && \
gcloud config get-value project && \
echo "=== Enabled APIs ===" && \
gcloud services list --enabled --filter="name:run.googleapis.com OR name:artifactregistry.googleapis.com OR name:compute.googleapis.com OR name:secretmanager.googleapis.com" --format="value(name)" && \
echo "=== Artifact Registry ===" && \
gcloud artifacts repositories list --location=asia-northeast1 --format="value(name)" && \
echo "=== Service Accounts ===" && \
gcloud iam service-accounts list --filter="email:github-actions@*.iam.gserviceaccount.com" --format="value(email)" && \
echo "=== Secret Manager ===" && \
gcloud secrets list --format="value(name)" && \
echo "=== Terraform State Bucket ===" && \
gsutil ls gs://$PROJECT_ID-terraform-state && \
echo "=== Cloud Armor Policies ===" && \
gcloud compute security-policies list --format="value(name)" && \
echo "=== Static IP Addresses ===" && \
gcloud compute addresses list --global --format="table(name,address,status)"
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

新しい二階層アーキテクチャで以下が利用可能になります：

### 🚀 初回セットアップ後の流れ
1. ✅ **共有インフラのセットアップ**: `infrastructure.yml` ワークフロー実行
2. ✅ **streamlit-sample-appのテストデプロイ**: 個別アプリワークフロー実行
3. ✅ **IP制限の動作確認**: 設定したIPからのみアクセス可能か確認

### 🏗️ 日常的な開発・運用
1. ✅ **新アプリ作成**: テンプレートから即座にデプロイ可能
2. ✅ **IP制限変更**: `terraform/shared/terraform.tfvars` 編集 → `infrastructure.yml` 実行のみ
3. ✅ **独立アプリ管理**: 各アプリの更新は他に影響なし
4. ✅ **静的IP**: 各アプリに固定IPアドレス付与

### 🎯 新アーキテクチャの恩恵
- **運用コスト削減**: IP変更が1回のワークフロー実行のみ
- **開発者体験向上**: 新アプリ作成が以前と同じ簡単さ
- **信頼性向上**: Terraform状態永続化で409エラー解消
- **セキュリティ強化**: 一元管理されたIP制限

apps-hubモノリポでの効率的な開発・運用をお楽しみください！

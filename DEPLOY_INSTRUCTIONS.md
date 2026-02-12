# Google Cloud Run Deployment Instructions

Google Cloud アプリケーション実行プロダクト（Cloud Run）を利用するための手順です。
作成した `cloud_backend` ディレクトリ内のコードを Cloud Run にデプロイし、AI分析機能をクラウド上で実行します。

## 1. 前提条件

- Google Cloud プロジェクトが作成されていること
- Google Cloud SDK (gcloud CLI) がインストールされ、ログインしていること
- 課金が有効になっていること

## 2. 必要なAPIの有効化

以下のコマンドを実行して、Cloud Run と Artifact Registry API を有効にします。

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

## 3. Cloud Run へのデプロイ

`cloud_backend` ディレクトリに移動し、以下のコマンドでデプロイします。

**【推奨】ビルドとデプロイを分けて実行する方法**
(権限エラー `PERMISSION_DENIED` を回避するため、専用リポジトリを作成してデプロイします)

```bash
# 1. コンテナリポジトリの作成 (初回のみ)
gcloud artifacts repositories create senp-ai-repo --repository-format=docker --location=asia-northeast1 --description="Docker repository for SENP AI"

# 2. サービスアカウントに権限付与 (ビルドエラー回避のため)
# エラーログに表示されたサービスアカウントIDを使用
gcloud projects add-iam-policy-binding semp-ai --member=serviceAccount:715552461794-compute@developer.gserviceaccount.com --role=roles/artifactregistry.writer

# 3. コンテナイメージのビルド
gcloud builds submit --tag asia-northeast1-docker.pkg.dev/semp-ai/senp-ai-repo/senp-ai-backend --region=asia-northeast1 .

# 4. イメージを指定してデプロイ
gcloud run deploy senp-ai-backend --image asia-northeast1-docker.pkg.dev/semp-ai/senp-ai-repo/senp-ai-backend --region asia-northeast1 --allow-unauthenticated
```

**【参考】ソースから直接デプロイする方法 (エラーが出やすい)**

```bash
gcloud run deploy senp-ai-backend --source . --region asia-northeast1 --allow-unauthenticated
```

※ もし `PERMISSION_DENIED` エラーが出る場合は、上記の【推奨】手順をお試しください。
※ `--allow-unauthenticated` は認証なしでアクセス可能にする設定です。セキュリティ要件に応じて変更してください（ハッカソン用であれば簡易化のためこの設定が多いです）。

デプロイが成功すると、以下のような Service URL が表示されます。
`Service parameters: ... URL: https://senp-ai-backend-xxxxxxxx-an.a.run.app`

## 4. 環境変数の設定 (重要)

Gemini API を利用するため、Google Cloud Console または以下のコマンドで API キーを設定する必要があります。

```bash
gcloud run services update senp-ai-backend --set-env-vars GOOGLE_API_KEY=あなたのAPIキー
```

## 5. クライアントアプリの設定

デスクトップアプリ (`run.py` または `controller_1120_01.py`) からクラウド上のAIを利用するには、環境変数 `SENP_AI_BACKEND_URL` に取得した Service URL を設定するか、コード内で指定します。

Windows (PowerShell):

```powershell
$env:SENP_AI_BACKEND_URL="https://senp-ai-backend-xxxxxxxx-an.a.run.app"
python run.py
```

## ディレクトリ構成

- `cloud_backend/`: Cloud Run 用のバックエンドコード
  - `main.py`: Flask アプリケーション
  - `ai_logic.py`: AI処理ロジック (AIModule)
  - `Dockerfile`: コンテナ定義
  - `requirements.txt`: 依存ライブラリ
- `ai_cloud_client.py`: クライアント側（デスクトップアプリ）からクラウドAPIを呼び出すためのモジュール

この構成により、Google Cloud の実行環境要件を満たすことができます。

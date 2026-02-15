# SENP_AI（センパイ）: 迷えるPC操作を「矢印」で導くAIアシスタント

![Project Status](https://img.shields.io/badge/Status-Review-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![Gemini](https://img.shields.io/badge/AI-Gemini_3_Flash-orange)
![Google Cloud](https://img.shields.io/badge/Backend-Cloud_Run-red)

## 概要 (Overview)

**SENP_AI（センプアイ）**は、PC操作に不慣れなユーザーや、新しいツールの操作に迷うユーザーのために開発された、**画面オーバーレイ型AIアシスタント**です。
ユーザーの「どこを押せばいいの？」という質問に対し、言葉での説明だけでなく、画面上に直接**「赤い矢印」**を表示して、直感的に操作を誘導します。

Google Cloud Run 上のバックエンドで **Gemini 3 Flash** (最新モデル) を動作させ、マルチモーダル（画像・テキスト・音声）での解析と、高精度な座標特定を実現しています。

---
**※ 本プロジェクトは「Agentic AI Hackathon with Google Cloud」の参加作品です。**

## 主な機能 (Features)

* **🎯 矢印による直感ガイド (Visual Grounding)**:
  * 「設定はどこ？」と聞くと、Geminiが画面を解析し、該当するボタンやメニューの位置に**赤い矢印**をオーバーレイ表示します。
  * 言葉を読む必要がなく、見たまま操作できます。

* **🤖 最新AIモデル搭載**:
  * **Gemini 3 Flash** を採用。高速なレスポンスと高いマルチモーダル認識能力で、複雑なUIも正確に理解します。
  * Cloud Run (Serverless) バックエンドにより、スケーラブルかつ安価に運用可能です。

* **📜 縦長ページ対応 (自動スクロール)**:
  * Webサイトなど一画面に収まらない場合、「全体を見て」「下の方も確認して」と指示すると、自動でスクロールしながら複数枚のスクリーンショットを撮影・結合して解析します。

* **🗣️ 音声対話 (Voice Interaction)**:
  * キーボード入力すら面倒な時、マイクボタン一つで質問可能。回答も音声合成(TTS)で読み上げられ、ハンズフリーに近い操作感を実現しています。

## システム構成 (Architecture)

```mermaid
graph LR
    User[Desktop Client] -- 画像 + 質問/音声 --> CloudRun[Cloud Run (Python/Flask)]
    CloudRun -- マルチモーダル解析 --> Gemini[Gemini 3 Flash]
    Gemini -- 座標データ + 回答 --> CloudRun
    CloudRun -- レスポンス --> User
    User -- 矢印描画/音声合成 --> Screen[画面オーバーレイ]
```

### 技術スタック

* **Backend**: Python (Flask), Google Cloud Run
* **AI**: Google GenAI SDK v1.0 (Gemini 3 Flash)
* **Frontend**: Python (CustomTkinter)
* **Tools**: SpeechRecognition, gTTS/pyttsx3, PyAutoGUI, Pillow

## 使い方 (Usage)

1. **クライアント起動**:

    ```bash
    python run.py
    ```

2. **質問**:
    * テキスト入力をするか、マイクアイコンを押して音声で「○○の設定はどこ？」などと質問します。
3. **ガイド**:
    * AIが画面を解析し、操作すべき場所に**赤い矢印**が表示されます。
    * 必要に応じて音声で補足説明をしてくれます。

## 環境構築 (Setup)

### 1. 前提条件

* Python 3.10 以上
* Google Cloud Project (バックエンドデプロイ用)
* **推奨**: Cloud RunのエンドポイントURL (環境変数 `SENP_AI_BACKEND_URL` に設定)

### 2. インストール (Local Client)

```bash
# リポジトリのクローン
git clone <repository-url>
cd SENP_AI_G_HKSN

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. 設定 (Environment Variables)

**Cloud Run (推奨)**:

```powershell
$env:SENP_AI_BACKEND_URL="https://your-cloud-run-service-url"
```

**Local Mode (API Key直接利用)**:

```powershell
$env:GOOGLE_API_KEY="your-gemini-api-key"
```

## ディレクトリ構成

```
SENP_AI_G_HKSN/
├── cloud_backend/      # Cloud Run用バックエンド (Flask + Gemini SDK)
│   ├── main.py
│   ├── ai_logic.py     # Gemini 3 Flash との通信ロジック
│   └── Dockerfile
├── run.py              # クライアントアプリ起動スクリプト
├── controller.py       # アプリのメイン制御ロジック
├── ui.py               # CustomTkinter製UI (オーバーレイ表示含む)
├── ai_client.py        # バックエンドとの通信クライアント
├── speech.py           # 音声認識モジュール
└── tts.py              # 音声合成モジュール
```

## ライセンス

MIT License

---
*Created by [Your Name / Team Name] for Agentic AI Hackathon with Google Cloud (2026)*

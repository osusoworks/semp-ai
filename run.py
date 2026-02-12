"""
SENP_AI - Main Entry Point (Version 1120_01)
メイン実行ファイル
"""

import sys
import os

# 必要なパッケージのインポートチェック
try:
    from controller_1120_01 import SENPAI_Controller
except ImportError as e:
    print(f"エラー: 必要なモジュールが見つかりません: {e}")
    print("\n以下のコマンドで依存パッケージをインストールしてください:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def check_api_key():
    """Google Gemini APIキーの確認"""
    # クラウドバックエンドモードの場合はAPIキー不要
    if os.environ.get("SENP_AI_BACKEND_URL"):
        print("✓ クラウドバックエンドモードで起動します (Local API Key 不要)")
        return

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("エラー: GOOGLE_API_KEY または GEMINI_API_KEY 環境変数が設定されていません。")
        print("※ クラウドバックエンドを使用する場合は SENP_AI_BACKEND_URL を設定してください。")
        print("\n以下の手順で設定してください:")
        print("1. Google AI Studio (https://aistudio.google.com/) でAPIキーを取得")
        print("2. 環境変数を設定:")
        print("   Windows: set GOOGLE_API_KEY=your-api-key")
        print("   Mac/Linux: export GOOGLE_API_KEY=your-api-key")
        sys.exit(1)

def main():
    """メイン関数"""
    print("=" * 60)
    print("SENP_AI - AI Assistant (Gemini Version)")
    print("=" * 60)
    print()
    
    # APIキーチェック
    check_api_key()
    
    print("✓ Google Gemini APIキー確認完了")
    print("✓ アプリケーション起動中...")
    print()
    print("Powered by Google Gemini:")
    print("  - Gemini 3 Flash (最新・推奨)")
    print("  - Gemini 3 Pro / 2.5シリーズも選択可能")
    print("  - 音声入力・音声出力対応")
    print()
    
    # コントローラー起動
    controller = SENPAI_Controller()
    controller.run()

if __name__ == "__main__":
    main()


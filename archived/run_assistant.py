"""
SENPAI Assistant - Main Entry Point
シンプルなAIアシスタント版のメイン実行ファイル
"""

import sys
import os

# 必要なパッケージのインポートチェック
try:
    from main_controller_assistant import AssistantController
except ImportError as e:
    print(f"エラー: 必要なモジュールが見つかりません: {e}")
    print("\n以下のコマンドで依存パッケージをインストールしてください:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def check_api_key():
    """OpenAI APIキーの確認"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("エラー: OPENAI_API_KEY環境変数が設定されていません。")
        print("\n以下の手順で設定してください:")
        print("1. OpenAIのAPIキーを取得")
        print("2. 環境変数を設定:")
        print("   Windows: set OPENAI_API_KEY=your-api-key")
        print("   Mac/Linux: export OPENAI_API_KEY=your-api-key")
        sys.exit(1)

def main():
    """メイン関数"""
    print("=" * 60)
    print("SENPAI - AI Assistant")
    print("=" * 60)
    print()
    
    # APIキーチェック
    check_api_key()
    
    print("✓ OpenAI APIキー確認完了")
    print("✓ アプリケーション起動中...")
    print()
    
    # コントローラー起動
    controller = AssistantController()
    controller.run()

if __name__ == "__main__":
    main()


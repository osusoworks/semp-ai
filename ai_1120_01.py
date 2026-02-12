"""
AI Module for SENP_AI (Version 1120_01)
Google Gemini専用 AI分析モジュール
ハッカソン対応版
"""

import os
from PIL import Image

# Google Generative AI (Gemini) のインポート
try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai がインストールされていません")
    print("pip install google-generativeai を実行してください")
    genai = None

class AIModule:
    # 利用可能なGeminiモデル一覧（2026年最新）
    AVAILABLE_MODELS = [
        ("gemini-3-flash-preview", "Gemini 3 Flash Preview ⚡ (最新)"),
        ("gemini-3-pro-preview", "Gemini 3 Pro Preview (最高性能)"),
        ("gemini-2.5-flash", "Gemini 2.5 Flash (高速・安定)"),
        ("gemini-2.5-pro", "Gemini 2.5 Pro (高精度・安定)"),
        ("gemini-2.0-flash", "Gemini 2.0 Flash (安定版)"),
        ("gemini-2.0-flash-lite", "Gemini 2.0 Flash Lite (低コスト)"),
    ]
    
    def __init__(self, model="gemini-3-flash-preview"):
        """
        AIモジュールの初期化
        
        Args:
            model: 使用するGeminiモデル名（デフォルト: gemini-3-flash）
        """
        # APIキーの取得
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY または GEMINI_API_KEY 環境変数が設定されていません。\n"
                "Google AI Studio (https://aistudio.google.com/) でAPIキーを取得してください。"
            )
        
        if genai is None:
            raise ImportError(
                "google-generativeai ライブラリがインストールされていません。\n"
                "pip install google-generativeai を実行してください。"
            )
        
        # Gemini APIの設定
        genai.configure(api_key=api_key)
        self.model = model
        self.genai_model = genai.GenerativeModel(model)
        print(f"AI Module initialized with Gemini model: {model}")
    
    def set_model(self, model):
        """
        使用するモデルを変更
        
        Args:
            model: 新しいモデル名
        """
        self.model = model
        self.genai_model = genai.GenerativeModel(model)
        print(f"Model changed to: {model}")
    
    def get_model(self):
        """現在のモデル名を取得"""
        return self.model
    
    @staticmethod
    def get_available_models():
        """利用可能なモデルのリストを取得"""
        return AIModule.AVAILABLE_MODELS
    
    def analyze_screen(self, screenshot_path, user_question):
        """
        スクリーンショットを分析して質問に回答
        
        Args:
            screenshot_path: スクリーンショット画像のパス、またはパスのリスト
            user_question: ユーザーの質問
            
        Returns:
            dict: {
                "success": bool,
                "answer": str,
                "model": str,
                "error": str (エラー時のみ),
                "target_box": list (if detected)
            }
        """
        try:
            # 画像を読み込み (リスト対応)
            images = []
            if isinstance(screenshot_path, list):
                for path in screenshot_path:
                    images.append(Image.open(path))
            else:
                images.append(Image.open(screenshot_path))
            
            # システムプロンプト
            system_prompt = """あなたはSENP_AIという画面分析AIアシスタントです。
ユーザーの画面を見て、質問に丁寧に答えてください。
こちらはWebページなどをスクロールして撮影した複数の画像（上から順）である可能性があります。
その場合は、画像全体を通してページの内容を理解し、質問に答えてください。
また、ユーザーが操作を行って画面が変化した後に、続きの指示を出す「ナビゲーションモード」が存在します。

回答のガイドライン:
- 画面に表示されている内容を正確に分析
- 具体的で分かりやすい説明
- 必要に応じて手順を示す
- 日本語で回答
- 親切で丁寧な口調
- 重要: 出力に「**」などのマークダウンによる強調（太字）は使用しないでください。プレーンテキストで回答してください。
- もし回答の中で、ユーザーが画面上の特定の場所（ボタンやアイコンなど）を見るべき、または操作すべきだと判断した場合は、その要素のバウンディングボックス（0-1000のスケール）を検出し、回答の最後に必ず「[TARGET_BOX: y_min, x_min, y_max, x_max]」という形式で追記してください。
  ※座標は「1枚目の画像」を基準にしてください。もし対象が2枚目以降にある場合は、その旨を言葉で補足し、BOXは出力しないでください（座標がずれるため）。
  例: 「画面左上の「新しいプロジェクト」ボタンをクリックしてください。[TARGET_BOX: 100, 200, 150, 300]」

- もし回答が「一連の操作手順の途中」であり、ユーザーが操作した後の画面を見て続きを説明する必要がある場合は、回答の最後に必ず「[CONTINUE]」と追記してください。
- 逆に、手順が完了した場合や、単発の質問で終わる場合は「[CONTINUE]」は不要です。"""
            
            # Gemini APIで画像分析
            content = [system_prompt, f"\n\nユーザーの質問: {user_question}"]
            content.extend(images)
            
            response = self.genai_model.generate_content(content)
            
            answer = response.text
            
            # 座標抽出
            import re
            target_box = None
            box_match = re.search(r"\[TARGET_BOX: (\d+), (\d+), (\d+), (\d+)\]", answer)
            if box_match:
                # y_min, x_min, y_max, x_max
                target_box = [int(box_match.group(1)), int(box_match.group(2)), int(box_match.group(3)), int(box_match.group(4))]
                answer = answer.replace(box_match.group(0), "").strip()

            # 継続フラグ抽出
            continue_navigation = False
            if "[CONTINUE]" in answer:
                continue_navigation = True
                answer = answer.replace("[CONTINUE]", "").strip()

            return {
                "success": True,
                "answer": answer.replace("[SHOW_ARROW]", "").strip(), # 旧コマンドも念のため除去
                "model": self.model,
                "target_box": target_box,
                "continue_navigation": continue_navigation
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"AI Analysis Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "model": self.model
            }


# テスト用
if __name__ == "__main__":
    print("=== SENP_AI - Gemini AI Module Test ===")
    print("\nAvailable Models:")
    for model_id, model_name in AIModule.get_available_models():
        print(f"  - {model_id}: {model_name}")
    
    # モジュール初期化（環境変数が設定されている場合のみ）
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        ai = AIModule()
        print(f"\nCurrent model: {ai.get_model()}")
        
        # モデル変更テスト
        ai.set_model("gemini-1.5-flash")
        print(f"Changed model: {ai.get_model()}")
    else:
        print("\n環境変数 GOOGLE_API_KEY または GEMINI_API_KEY が設定されていません")

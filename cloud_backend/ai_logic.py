"""
AI Module for SENP_AI Cloud Backend
Google Gemini専用 AI分析モジュール (Cloud Run対応版)
"""

import os
import io
from PIL import Image

# Google Generative AI (Gemini) のインポート
try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai がインストールされていません")
    genai = None

class AIModule:
    # 利用可能なGeminiモデル一覧（2026年最新）
    AVAILABLE_MODELS = [
        ("gemini-3.0-flash", "Gemini 3 Flash (最新・最高速)"),
        ("gemini-3.0-pro", "Gemini 3 Pro (最新・最高精度)"),
        ("gemini-2.0-flash", "Gemini 2.0 Flash (安定・高速)"),
        ("gemini-2.0-pro", "Gemini 2.0 Pro (高性能)"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash (軽量版)"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro (旧世代・高精度)"),
    ]
    
    def __init__(self, model=None):
        """
        AIモジュールの初期化
        """
        # モデル名の取得 (環境変数 -> 引数 -> デフォルト)
        self.model = os.environ.get("GEMINI_MODEL") or model or "gemini-3.0-flash"
        
        # APIキーの取得
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            # Cloud Runのログに出力されるようにprintを使用
            print("WARNING: GOOGLE_API_KEY is not set.")
        
        if genai is None:
            raise ImportError("google-generativeai library is missing.")
        
        # Gemini APIの設定
        if api_key:
            genai.configure(api_key=api_key)
            
        # self.genai_model は analyze_images 内で生成するようにするため、ここでは初期化のみ
        print(f"AI Module initialized with default Gemini model: {self.model}")
    
    def analyze_images(self, images, user_question, model_override=None):
        """
        画像オブジェクトのリストを分析して質問に回答
        """
        try:
            # 使用するモデルを決定
            target_model = model_override or self.model
            print(f"Analyzing with model: {target_model}")
            gen_model = genai.GenerativeModel(target_model)
            
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
            
            response = gen_model.generate_content(content)
            
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
                "answer": answer.replace("[SHOW_ARROW]", "").strip(),
                "model": target_model,
                "target_box": target_box,
                "continue_navigation": continue_navigation
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"AI Analysis Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "model": target_model if 'target_model' in locals() else self.model
            }

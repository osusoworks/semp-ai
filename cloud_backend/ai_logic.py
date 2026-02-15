import os
import io
import json
import re
from google import genai
from google.genai import types
from PIL import Image

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
    
    def __init__(self, model="gemini-3.0-flash"):
        """
        AIモジュールの初期化
        """
        # APIキーの取得
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY not set. Please set GOOGLE_API_KEY environment variable.")
        
        if genai is None:
            raise ImportError("google-genai library is missing.")
        
        # Gemini APIクライアントの設定
        self.client = genai.Client(api_key=api_key)
        self.model = model
        print(f"AI Module initialized with Gemini model: {model}")
    
    def analyze_images(self, images, user_question, model_override=None):
        """
        画像オブジェクトのリストを分析して質問に回答
        
        Args:
            images: PIL.Image オブジェクトのリスト
            user_question: ユーザーの質問
            model_override: 使用するモデル名（オーバーライド）
            
        Returns:
            dict: 結果
        """
        # 使用するモデルを決定
        use_model = model_override if model_override else self.model
        
        try:
            # システムプロンプト
            system_prompt = """あなたはSENP_AIという画面分析AIアシスタントです。
ユーザーの画面を見て、質問に丁寧に答えてください。
こちらはWebページなどをスクロールして撮影した複数の画像（上から順）である可能性があります。
その場合は、画像全体を通してページの内容を理解し、質問に答えてください。

回答のガイドライン:
- 画面に表示されている内容を正確に分析
- もし質問の答えが画面上の情報に見つからない場合は、あなたの持つ一般知識を使って回答してください
- 画面外の知識を使用する場合、「画面にはありませんが」等の前置きは不要です
- 具体的で分かりやすい説明
- 必要に応じて手順を示す
- 日本語で回答
- 親切で丁寧な口調
- 専門用語が出た際は、初心者にもわかるように補足説明を加えてください。
- あなたは「PCに詳しい頼れる先輩」です。わからないことは適当に答えず、検索機能を使って調べ、正確な回答を心がけてください。
- 重要: 出力に「**」などのマークダウンによる強調（太字）は使用しないでください。プレーンテキストで回答してください。

バウンディングボックスについて:
もし回答の中で、ユーザーが画面上の特定の場所（ボタンやアイコンなど）を見るべき、または操作すべきだと判断した場合は、
その要素の正確なバウンディングボックスを検出し、回答の最後に追記してください。

座標のルール:
- 座標は画像全体を基準にした0-1000のスケールで指定してください
- フォーマット: [TARGET_BOX: y_min, x_min, y_max, x_max]
- y_min: 対象要素の上端のy座標 (0=画像の上端, 1000=画像の下端)
- x_min: 対象要素の左端のx座標 (0=画像の左端, 1000=画像の右端)
- y_max: 対象要素の下端のy座標
- x_max: 対象要素の右端のx座標
- ボックスは対象の要素をぴったり囲むように指定してください
- もし対象が2枚目以降の画像にある場合は、BOXは出力せず言葉で補足してください

例:
- 画面中央のボタン(画面の50%の位置): [TARGET_BOX: 470, 450, 530, 550]
- 画面左上の小さなアイコン: [TARGET_BOX: 50, 30, 100, 80]
- 画面右下のボタン: [TARGET_BOX: 900, 850, 950, 950]"""
            
            # コンテンツの構築
            contents = [system_prompt, f"\n\nユーザーの質問: {user_question}"]
            
            # 画像をcontentsに追加
            for img in images:
                contents.append(img)
            
            # Gemini APIで画像分析
            response = self.client.models.generate_content(
                model=use_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_modalities=["TEXT"]
                )
            )
            
            answer = response.text
            
            # 座標抽出
            target_box = None
            box_match = re.search(r"\[TARGET_BOX:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]", answer)
            if box_match:
                # y_min, x_min, y_max, x_max
                target_box = [int(box_match.group(1)), int(box_match.group(2)), int(box_match.group(3)), int(box_match.group(4))]
                answer = answer.replace(box_match.group(0), "").strip()
                print(f"DEBUG: Extracted TARGET_BOX: {target_box}")

            # 継続フラグ抽出
            continue_navigation = False
            if "[CONTINUE]" in answer:
                continue_navigation = True
                answer = answer.replace("[CONTINUE]", "").strip()

            return {
                "success": True,
                "answer": answer.replace("[SHOW_ARROW]", "").strip(),
                "model": use_model,
                "target_box": target_box,
                "continue_navigation": continue_navigation
            }

        except Exception as e:
            error_msg = str(e)
            print(f"AI Analysis Error: {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": error_msg,
                "model": use_model
            }


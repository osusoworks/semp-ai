import os
import io
import json
from google import genai
from google.genai import types
from PIL import Image

class AIModule:
    def __init__(self, model="gemini-2.0-flash"): # 3-flash-previewが不安定な場合は2.0-flashが安定
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API Key is missing.")
        
        # 新SDKクライアント
        self.client = genai.Client(api_key=api_key)
        self.model_id = model
        print(f"AI Module (New SDK) initialized with: {self.model_id}")

    def _pil_to_bytes(self, pil_img):
        """PIL画像をバイトに変換"""
        img_byte_arr = io.BytesIO()
        pil_img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def analyze_images(self, images, user_question):
        try:
            # システムプロンプト (JSON形式を指示)
            system_prompt = """あなたはSENP_AIという画面分析AIアシスタントです。
以下のJSONフォーマットで回答してください。
{
  "answer": "ユーザーへの回答テキスト（プレーンテキスト、太字**は禁止）",
  "target_box": [y_min, x_min, y_max, x_max], // 操作箇所がある場合のみ(0-1000)、ないならnull
  "continue_navigation": true // 続きの操作が必要ならtrue
}"""

            # コンテンツ構築
            contents = [types.Part.from_text(text=system_prompt + f"\n\nユーザーの質問: {user_question}")]
            
            # 複数画像をPartに追加
            for img in images:
                contents.append(types.Part.from_bytes(
                    data=self._pil_to_bytes(img),
                    mime_type="image/jpeg"
                ))

            # 生成設定
            config = types.GenerateContentConfig(
                response_mime_type="application/json"
            )

            # 実行
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )

            # 結果のパース
            res_data = json.loads(response.text)
            return {
                "success": True,
                "answer": res_data.get("answer", ""),
                "model": self.model_id,
                "target_box": res_data.get("target_box"),
                "continue_navigation": res_data.get("continue_navigation", False)
            }

        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return {"success": False, "error": str(e), "model": self.model_id}
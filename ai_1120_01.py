"""
AI Module for SENP_AI (Version 1120_01)
モデル選択機能付きAI分析モジュール
"""

import os
import base64
from openai import OpenAI

class AIModule:
    # 利用可能なモデル一覧
    AVAILABLE_MODELS = [
        ("gpt-5.1-instant", "GPT-5.1 Instant ⚡ (最新・推奨)"),
        ("gpt-5.1", "GPT-5.1 (最新・高精度)"),
        ("gpt-5", "GPT-5 (高精度)"),
        ("gpt-5-instant", "GPT-5 Instant ⚡"),
        ("gpt-4.1", "GPT-4.1 (高精度)"),
        ("gpt-4.1-mini", "GPT-4.1 Mini (高速)"),
        ("gpt-4o", "GPT-4o (安定)"),
        ("gpt-4o-mini", "GPT-4o Mini (高速・低コスト)"),
    ]
    
    def __init__(self, model="gpt-5.1-instant"):
        """
        AIモジュールの初期化
        
        Args:
            model: 使用するGPTモデル名（デフォルト: gpt-5.1-instant）
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model
        print(f"AI Module initialized with model: {model}")
    
    def set_model(self, model):
        """
        使用するモデルを変更
        
        Args:
            model: 新しいモデル名
        """
        self.model = model
        print(f"Model changed to: {model}")
    
    def get_model(self):
        """現在のモデル名を取得"""
        return self.model
    
    @staticmethod
    def get_available_models():
        """利用可能なモデルのリストを取得"""
        return AIModule.AVAILABLE_MODELS
    
    def encode_image(self, image_path):
        """
        画像をBase64エンコード
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            Base64エンコードされた画像データ
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_screen(self, screenshot_path, user_question):
        """
        スクリーンショットを分析して質問に回答
        
        Args:
            screenshot_path: スクリーンショット画像のパス
            user_question: ユーザーの質問
            
        Returns:
            dict: {
                "success": bool,
                "answer": str,
                "model": str,
                "error": str (エラー時のみ)
            }
        """
        try:
            # 画像をBase64エンコード
            base64_image = self.encode_image(screenshot_path)
            
            # OpenAI APIでビジョン分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """あなたはSENP_AIという画面分析AIアシスタントです。
ユーザーの画面を見て、質問に丁寧に答えてください。

回答のガイドライン:
- 画面に表示されている内容を正確に分析
- 具体的で分かりやすい説明
- 必要に応じて手順を示す
- 日本語で回答
- 親切で丁寧な口調"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_question
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "success": True,
                "answer": answer,
                "model": self.model
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
    print("=== SENP_AI - AI Module Test ===")
    print("\nAvailable Models:")
    for model_id, model_name in AIModule.get_available_models():
        print(f"  - {model_id}: {model_name}")
    
    # モジュール初期化
    ai = AIModule()
    print(f"\nCurrent model: {ai.get_model()}")
    
    # モデル変更テスト
    ai.set_model("gpt-4o-mini")
    print(f"Changed model: {ai.get_model()}")


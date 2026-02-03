"""
AI Module for SENP_AI (Version 1120_02 - Context-Aware)
会話履歴を保持し、文脈を理解するAI分析モジュール
"""

import os
import base64
from openai import OpenAI

class ContextAwareAIModule:
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
        
        # 会話履歴を保持
        self.conversation_history = []
        
        # スクリーンショット履歴を保持
        self.screenshot_history = []
        
        # システムプロンプトを設定
        self._initialize_system_prompt()
        
        print(f"Context-Aware AI Module initialized with model: {model}")
    
    def _initialize_system_prompt(self):
        """システムプロンプトを初期化"""
        system_message = {
            "role": "system",
            "content": """あなたはSENP_AIという画面分析AIアシスタントです。
ユーザーの画面を見て、質問に丁寧に答えてください。

重要な特徴:
- **会話の文脈を理解する**: 前の質問・回答を覚えていて、「それ」「あれ」などの指示語を理解する
- **複数の画面を参照**: ユーザーが複数のスクリーンショットを見せた場合、「最初の画面」「さっきの画面」などを区別する
- **自然な対話**: チャットのように自然に会話を続ける

回答のガイドライン:
- 画面に表示されている内容を正確に分析
- 前の会話の内容を踏まえた回答
- 具体的で分かりやすい説明
- 必要に応じて手順を示す
- 日本語で回答
- 親切で丁寧な口調
- 「それ」「あれ」などの指示語は文脈から判断"""
        }
        self.conversation_history.append(system_message)
    
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
        return ContextAwareAIModule.AVAILABLE_MODELS
    
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
    
    def add_screenshot(self, screenshot_path):
        """
        スクリーンショットを履歴に追加
        
        Args:
            screenshot_path: スクリーンショット画像のパス
            
        Returns:
            スクリーンショットのインデックス（何番目か）
        """
        self.screenshot_history.append(screenshot_path)
        return len(self.screenshot_history)
    
    def analyze_with_context(self, user_question, screenshot_path=None):
        """
        会話履歴を考慮して画面を分析
        
        Args:
            user_question: ユーザーの質問
            screenshot_path: スクリーンショット画像のパス（オプション）
            
        Returns:
            dict: {
                "success": bool,
                "answer": str,
                "model": str,
                "context_length": int,  # 会話履歴の長さ
                "error": str (エラー時のみ)
            }
        """
        try:
            # ユーザーメッセージを構築
            user_message_content = []
            
            # テキスト質問を追加
            user_message_content.append({
                "type": "text",
                "text": user_question
            })
            
            # 新しいスクリーンショットがある場合は追加
            if screenshot_path:
                screenshot_index = self.add_screenshot(screenshot_path)
                base64_image = self.encode_image(screenshot_path)
                user_message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high"
                    }
                })
                
                # スクリーンショット番号を質問に追加
                if screenshot_index > 1:
                    user_message_content[0]["text"] += f"\n\n（これは{screenshot_index}番目のスクリーンショットです）"
            
            # ユーザーメッセージを会話履歴に追加
            user_message = {
                "role": "user",
                "content": user_message_content
            }
            self.conversation_history.append(user_message)
            
            # OpenAI APIで分析（会話履歴全体を送信）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=2000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # アシスタントの回答を会話履歴に追加
            assistant_message = {
                "role": "assistant",
                "content": answer
            }
            self.conversation_history.append(assistant_message)
            
            return {
                "success": True,
                "answer": answer,
                "model": self.model,
                "context_length": len(self.conversation_history)
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"AI Analysis Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "model": self.model,
                "context_length": len(self.conversation_history)
            }
    
    def reset_conversation(self):
        """
        会話履歴をリセット
        """
        self.conversation_history = []
        self.screenshot_history = []
        self._initialize_system_prompt()
        print("Conversation history reset")
    
    def get_conversation_summary(self):
        """
        会話履歴のサマリーを取得
        
        Returns:
            dict: {
                "total_messages": int,
                "user_messages": int,
                "assistant_messages": int,
                "screenshots": int
            }
        """
        user_count = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        assistant_count = sum(1 for msg in self.conversation_history if msg["role"] == "assistant")
        
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "screenshots": len(self.screenshot_history)
        }


# テスト用
if __name__ == "__main__":
    print("=== SENP_AI - Context-Aware AI Module Test ===")
    print("\nAvailable Models:")
    for model_id, model_name in ContextAwareAIModule.get_available_models():
        print(f"  - {model_id}: {model_name}")
    
    # モジュール初期化
    ai = ContextAwareAIModule()
    print(f"\nCurrent model: {ai.get_model()}")
    
    # 会話サマリー
    summary = ai.get_conversation_summary()
    print(f"\nConversation Summary: {summary}")
    
    # リセットテスト
    ai.reset_conversation()
    print("\nConversation reset completed")


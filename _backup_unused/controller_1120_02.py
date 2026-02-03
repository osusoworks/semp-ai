"""
Main Controller for SENP_AI (Version 1120_02 - Context-Aware)
会話履歴を保持するコンテキスト管理コントローラー
"""

import os
import time
from datetime import datetime
from ui_1120_02 import ContextAwareUI
from ai_1120_02 import ContextAwareAIModule
from speech_1120_01 import SpeechModule
from tts_1120_01 import TTSModule
from PIL import ImageGrab

class ContextAwareController:
    def __init__(self):
        """コントローラーの初期化"""
        # AIモジュール初期化（デフォルトモデル: gpt-5.1-instant）
        self.ai_module = ContextAwareAIModule(model="gpt-5.1-instant")
        self.speech_module = SpeechModule()
        self.tts_module = TTSModule()
        
        # UI初期化
        self.ui = ContextAwareUI(
            available_models=ContextAwareAIModule.get_available_models(),
            on_screenshot_callback=self.take_screenshot,
            on_question_callback=self.process_question,
            on_voice_input_callback=self.handle_voice_input,
            on_tts_toggle_callback=self.toggle_tts,
            on_model_change_callback=self.change_model,
            on_reset_conversation_callback=self.reset_conversation
        )
        
        self.current_screenshot = None
        self.tts_enabled = True
        
        # 起動メッセージ
        self.ui.add_message(
            "assistant",
            "こんにちは！SENP_AIです。\n\n✨ 新機能: 会話の文脈を理解します！\n\n"
            "「それ」「あれ」などの指示語が通じます。\n"
            "前の質問・回答を覚えているので、自然に会話を続けられます。\n\n"
            "まずはスクリーンショットを撮って、質問してください。",
            self._get_timestamp(),
            model=self.ai_module.get_model()
        )
        self._update_context_display()
        self.ui.set_status("準備完了", "green")
    
    def _get_timestamp(self):
        """現在時刻のタイムスタンプを取得"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _update_context_display(self):
        """会話コンテキスト情報を更新"""
        summary = self.ai_module.get_conversation_summary()
        self.ui.set_context_info(
            summary["user_messages"],
            summary["assistant_messages"],
            summary["screenshots"]
        )
    
    def take_screenshot(self):
        """スクリーンショットを撮影"""
        try:
            # スクリーンショット撮影
            screenshot = ImageGrab.grab()
            
            # 保存
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            
            self.current_screenshot = screenshot_path
            
            # スクリーンショット番号を取得
            screenshot_count = len(self.ai_module.screenshot_history) + 1
            
            self.ui.set_status(
                f"スクリーンショット保存完了 ({screenshot_count}枚目): {screenshot_path}", 
                "green"
            )
            
        except Exception as e:
            error_msg = f"スクリーンショットエラー: {str(e)}"
            print(error_msg)
            self.ui.set_status(error_msg, "red")
    
    def process_question(self, question):
        """質問を処理してAI回答を取得（会話履歴を考慮）"""
        try:
            # ユーザーメッセージを表示
            self.ui.add_message("user", question, self._get_timestamp())
            
            # AI分析（会話履歴を考慮）
            self.ui.set_status(f"AI分析中... (モデル: {self.ai_module.get_model()})", "blue")
            
            # 新しいスクリーンショットがある場合はそれを使用
            # ない場合はNoneを渡す（過去のスクリーンショットを参照可能）
            result = self.ai_module.analyze_with_context(
                user_question=question,
                screenshot_path=self.current_screenshot
            )
            
            # スクリーンショットを使用したらクリア
            if self.current_screenshot:
                self.current_screenshot = None
            
            if result["success"]:
                answer = result["answer"]
                model_used = result["model"]
                context_length = result["context_length"]
                
                self.ui.add_message("assistant", answer, self._get_timestamp(), model=model_used)
                
                # 会話コンテキスト情報を更新
                self._update_context_display()
                
                # TTS音声出力
                if self.tts_enabled:
                    self.tts_module.speak(answer)
                
                self.ui.set_status("準備完了", "green")
            else:
                error_msg = f"AI分析エラー: {result.get('error', '不明なエラー')}"
                self.ui.add_message("assistant", error_msg, self._get_timestamp())
                self.ui.set_status(error_msg, "red")
        
        except Exception as e:
            error_msg = f"処理エラー: {str(e)}"
            print(error_msg)
            self.ui.add_message("assistant", error_msg, self._get_timestamp())
            self.ui.set_status(error_msg, "red")
    
    def handle_voice_input(self):
        """音声入力を処理"""
        try:
            self.ui.set_status("音声入力中...", "blue")
            
            # 音声認識
            result = self.speech_module.listen()
            
            if result["success"]:
                recognized_text = result["text"]
                self.ui.set_input_text(recognized_text)
                self.ui.set_status("音声認識完了", "green")
                
                # 自動的に質問を送信
                time.sleep(0.5)
                self.process_question(recognized_text)
            else:
                error_msg = f"音声認識エラー: {result.get('error', '不明なエラー')}"
                self.ui.set_status(error_msg, "red")
        
        except Exception as e:
            error_msg = f"音声入力エラー: {str(e)}"
            print(error_msg)
            self.ui.set_status(error_msg, "red")
    
    def toggle_tts(self, enabled):
        """TTS ON/OFFを切り替え"""
        self.tts_enabled = enabled
        
        if not enabled and self.tts_module.is_speaking():
            self.tts_module.stop()
        
        status = "有効" if enabled else "無効"
        print(f"音声回答: {status}")
    
    def change_model(self, model_id):
        """AIモデルを変更"""
        self.ai_module.set_model(model_id)
        self.ui.set_status(f"モデル変更: {model_id}", "green")
        print(f"AI Model changed to: {model_id}")
    
    def reset_conversation(self):
        """会話履歴をリセット"""
        try:
            self.ui.set_status("会話をリセット中...", "blue")
            
            # AIモジュールの会話履歴をリセット
            self.ai_module.reset_conversation()
            
            # 現在のスクリーンショットをクリア
            self.current_screenshot = None
            
            # UI表示を更新
            self.ui.add_message("system", "会話履歴がリセットされました")
            self._update_context_display()
            
            self.ui.set_status("準備完了", "green")
            print("Conversation reset completed")
            
        except Exception as e:
            error_msg = f"リセットエラー: {str(e)}"
            print(error_msg)
            self.ui.set_status(error_msg, "red")
    
    def run(self):
        """アプリケーションを起動"""
        try:
            self.ui.run()
        except KeyboardInterrupt:
            print("\n終了します...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        print("クリーンアップ中...")
        self.tts_module.cleanup()
        print("完了")


if __name__ == "__main__":
    controller = ContextAwareController()
    controller.run()


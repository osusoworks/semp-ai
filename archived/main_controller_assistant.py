"""
Main Controller for SENPAI Assistant
シンプルなAIアシスタント版のメインコントローラー
"""

import os
import time
from datetime import datetime
from ui_module_assistant import AssistantUI
from ai_module_improved import AIModule
from speech_module import SpeechModule
from tts_module import TTSModule
from PIL import ImageGrab

class AssistantController:
    def __init__(self):
        """コントローラーの初期化"""
        self.ai_module = AIModule()
        self.speech_module = SpeechModule()
        self.tts_module = TTSModule()
        
        self.ui = AssistantUI(
            on_screenshot_callback=self.take_screenshot,
            on_question_callback=self.process_question,
            on_voice_input_callback=self.handle_voice_input,
            on_tts_toggle_callback=self.toggle_tts
        )
        
        self.current_screenshot = None
        self.tts_enabled = True
        
        # 起動メッセージ
        self.ui.add_message(
            "assistant",
            "こんにちは！SENPAIです。\n画面のスクリーンショットを撮って、質問してください。",
            self._get_timestamp()
        )
        self.ui.set_status("準備完了", "green")
    
    def _get_timestamp(self):
        """現在時刻のタイムスタンプを取得"""
        return datetime.now().strftime("%H:%M:%S")
    
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
            
            self.ui.set_status(f"スクリーンショット保存完了: {screenshot_path}", "green")
            
        except Exception as e:
            error_msg = f"スクリーンショットエラー: {str(e)}"
            print(error_msg)
            self.ui.set_status(error_msg, "red")
    
    def process_question(self, question):
        """質問を処理してAI回答を取得"""
        try:
            # ユーザーメッセージを表示
            self.ui.add_message("user", question, self._get_timestamp())
            
            # スクリーンショットがない場合
            if not self.current_screenshot:
                answer = "スクリーンショットが撮影されていません。まず「📸 スクリーンショット」ボタンをクリックしてください。"
                self.ui.add_message("assistant", answer, self._get_timestamp())
                self.ui.set_status("準備完了", "green")
                return
            
            # AI分析
            self.ui.set_status("AI分析中...", "blue")
            
            result = self.ai_module.analyze_screen(
                screenshot_path=self.current_screenshot,
                user_question=question
            )
            
            if result["success"]:
                answer = result["answer"]
                self.ui.add_message("assistant", answer, self._get_timestamp())
                
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
    controller = AssistantController()
    controller.run()


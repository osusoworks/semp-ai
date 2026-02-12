"""
TTS (Text-to-Speech) Module
OpenAI TTS APIを使用して音声出力を行うモジュール
"""

import os
from openai import OpenAI
from pathlib import Path
import tempfile
import threading
import pygame

class TTSModule:
    def __init__(self):
        """TTSモジュールの初期化"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.temp_dir = tempfile.gettempdir()
        self.is_playing = False
        self.current_thread = None
        
        # pygameのミキサーを初期化
        pygame.mixer.init()
        
    def speak(self, text, voice="nova", speed=1.0):
        """
        テキストを音声に変換して再生
        
        Args:
            text: 読み上げるテキスト
            voice: 音声の種類 (alloy, echo, fable, onyx, nova, shimmer)
            speed: 再生速度 (0.25 - 4.0)
        """
        if self.is_playing:
            self.stop()
        
        # 別スレッドで音声生成・再生
        self.current_thread = threading.Thread(
            target=self._speak_thread,
            args=(text, voice, speed)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def _speak_thread(self, text, voice, speed):
        """音声生成・再生のスレッド処理"""
        try:
            self.is_playing = True
            
            # OpenAI TTS APIで音声生成
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            
            # 一時ファイルに保存
            audio_file = Path(self.temp_dir) / "senpai_tts.mp3"
            response.stream_to_file(audio_file)
            
            # pygameで再生
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.play()
            
            # 再生完了まで待機
            while pygame.mixer.music.get_busy() and self.is_playing:
                pygame.time.Clock().tick(10)
            
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            self.is_playing = False
    
    def stop(self):
        """音声再生を停止"""
        self.is_playing = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    
    def is_speaking(self):
        """音声再生中かどうかを返す"""
        return self.is_playing
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.stop()
        pygame.mixer.quit()


# テスト用
if __name__ == "__main__":
    tts = TTSModule()
    print("音声テスト開始...")
    tts.speak("こんにちは。SENPAIです。画面を見て質問に答えます。")
    
    # 再生完了まで待機
    import time
    while tts.is_speaking():
        time.sleep(0.1)
    
    print("音声テスト完了")
    tts.cleanup()

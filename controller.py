import os
import time
import threading
from datetime import datetime
import pyautogui  # Added for scroll functionality
import cv2
import numpy as np
from ui import SENPAI_UI
from ai_client import RemoteAIModule # Cloud Run support
from speech import SpeechModule
from tts import TTSModule
from PIL import ImageGrab

class SENPAI_Controller:
    def __init__(self):
        """コントローラーの初期化"""
        # AIモジュール初期化 (Cloud Run版をデフォルトで使用)
        backend_url = os.environ.get("SENP_AI_BACKEND_URL")
        if backend_url:
            print(f"Using Cloud Backend AI: {backend_url}")
        else:
            print("WARNING: SENP_AI_BACKEND_URL not set. Using default localhost.")
        
        self.ai_module = RemoteAIModule(backend_url)
        
        # 音声認識モジュールの初期化（コールバックを指定）
        self.speech_module = SpeechModule(callback=self.on_speech_recognized)
        self.tts_module = TTSModule()
        
        # UI初期化
        self.ui = SENPAI_UI(
            available_models=RemoteAIModule.get_available_models(),
            on_question_callback=self.process_question,
            on_voice_input_callback=self.handle_voice_input,
            on_tts_toggle_callback=self.toggle_tts,
            on_model_change_callback=self.change_model
        )
        
        self.current_screenshot = None
        self.tts_enabled = True
        
        # ナビゲーション（追従モード）用変数
        self.is_navigating = False
        self.last_screen_array = None
        self.navigation_thread = threading.Thread(target=self._navigation_loop, daemon=True)
        self.navigation_thread.start()
        
        # 起動メッセージ

        self.ui.set_status("準備完了", "green")
    
    def _get_timestamp(self):
        """現在時刻のタイムスタンプを取得"""
        return datetime.now().strftime("%H:%M:%S")
    
    def take_screenshot(self, return_path=False):
        """スクリーンショットを撮影"""
        try:
            # スクリーンショット撮影
            screenshot = ImageGrab.grab()
            
            # 保存
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f") # ミリ秒まで入れて重複回避
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            
            self.screen_size = screenshot.size # (width, height)
            
            if return_path:
                return screenshot_path

            self.current_screenshot = screenshot_path
            self.ui.set_status(f"スクリーンショット保存完了: {screenshot_path}", "green")
            
        except Exception as e:
            error_msg = f"スクリーンショットエラー: {str(e)}"
            print(error_msg)
            self.ui.set_status(error_msg, "red")
            if return_path:
                return None

    def process_question(self, question):
        """質問を処理してAI回答を取得（自動スクロール判定含む）"""
        try:
            # ユーザーメッセージを表示
            self.ui.add_message("user", question, self._get_timestamp())
            
            # UIを一時的に非表示にしてスクリーンショットを撮影
            self.ui.hide_window()
            time.sleep(0.05)  # ウィンドウが消えるのを短時間待つ
            
            # キーワード判定
            scroll_keywords = ["全体", "全部", "続き", "スクロール", "下", "残りの", "ページ"]
            should_scroll = any(k in question for k in scroll_keywords)
            
            screenshot_data = None
            
            try:
                if should_scroll:
                    self.ui.set_status("ページ全体をキャプチャ中(スクロール)...", "blue")
                    screenshots = []
                    
                    # 1枚目
                    path1 = self.take_screenshot(return_path=True)
                    if path1: screenshots.append(path1)
                    
                    # 2枚目 (スクロール)
                    pyautogui.press('pagedown')
                    time.sleep(0.8) # 描画待ち
                    path2 = self.take_screenshot(return_path=True)
                    if path2: screenshots.append(path2)
                    
                    # 3枚目
                    pyautogui.press('pagedown')
                    time.sleep(0.8)
                    path3 = self.take_screenshot(return_path=True)
                    if path3: screenshots.append(path3)
                    
                    # 元に戻す
                    pyautogui.press('pageup')
                    pyautogui.press('pageup')
                    
                    screenshot_data = screenshots
                    self.current_screenshot = screenshots # 履歴用
                    
                else:
                    self.take_screenshot()
                    screenshot_data = self.current_screenshot
                    
            finally:
                # スクリーンショット撮影後（またはエラー時）に必ずUIを再表示
                self.ui.show_window()
            
            if not screenshot_data:
                self.ui.set_status("スクリーンショット撮影失敗", "red")
                return

            self._analyze_with_ai(question, screenshot_data)
        
        except Exception as e:
            error_msg = f"処理エラー: {str(e)}"
            print(error_msg)
            self.ui.add_message("assistant", error_msg, self._get_timestamp())
            self.ui.set_status(error_msg, "red")

    def _analyze_with_ai(self, question, screenshot_data):
        """AI分析の共通処理"""
        # AI分析
        self.ui.set_status(f"AI分析中... (モデル: {self.ai_module.get_model()})", "blue")
        
        # 質問が空の場合はデフォルトのプロンプトを設定
        actual_question = question if question else "画面全体の内容を要約して、何ができるページか教えてください。"

        result = self.ai_module.analyze_screen(
            screenshot_path=screenshot_data,
            user_question=actual_question
        )
        
        if result["success"]:
            answer = result["answer"]
            model_used = result["model"]
            self.ui.add_message("assistant", answer, self._get_timestamp(), model=model_used)
            
            # TTS音声出力
            if self.tts_enabled:
                self.tts_module.speak(answer)
            
            if result.get("target_box"):
                # ターゲットボックスがある場合、座標計算して矢印を表示
                # NOTE: スクロール撮影の場合、target_boxは1枚目の画像の座標として扱う前提
                # box: [y_min, x_min, y_max, x_max] (0-1000 scale)
                box = result["target_box"]
                y_min, x_min, y_max, x_max = box
                
                if hasattr(self, 'screen_size') and self.screen_size:
                    screen_w, screen_h = self.screen_size
                    
                    # ボックスの中心座標を計算
                    center_x = int((x_min + x_max) / 2 / 1000 * screen_w)
                    # ターゲットの上端(y_min)を指すようにする
                    target_top_y = int(y_min / 1000 * screen_h)
                    
                    self.ui.show_global_arrow(center_x, target_top_y)
                else:
                    pass 

            elif result.get("show_arrow", False):
                self.ui.show_tutorial_arrow()

            # ナビゲーションモード（追従）の判定
            if result.get("continue_navigation"):
                self.is_navigating = True
                self.ui.set_status("操作を待機中... (画面変化でAIが応答します)", "blue")
                # 現在の画面を基準画像として保存
                self._update_last_screen()
            else:
                self.is_navigating = False
                self.ui.set_status("準備完了", "green")
        else:
            error_msg = f"AI分析エラー: {result.get('error', '不明なエラー')}"
            self.ui.add_message("assistant", error_msg, self._get_timestamp())
            self.ui.set_status(error_msg, "red")
            self.is_navigating = False # エラー時は解除

    def _update_last_screen(self):
        """現在の画面をナビゲーション基準として保存"""
        try:
            screen = ImageGrab.grab()
            # 比較用に小さくリサイズしてグレースケール化
            screen_small = screen.resize((320, 240))
            self.last_screen_array = np.array(screen_small.convert('L'))
        except Exception:
            pass

    def _navigation_loop(self):
        """画面変化を監視するバックグラウンドループ"""
        while True:
            time.sleep(1.0) # 1秒ごとにチェック
            
            if not self.is_navigating or self.last_screen_array is None:
                continue
                
            # メイン処理中（AI分析中など）は動かないようにフラグチェックすべきだが、
            # 単純化のため、is_navigating が True の間だけ動作
            
            try:
                # 現在の画面を取得
                current_screen = ImageGrab.grab()
                current_small = current_screen.resize((320, 240))
                current_array = np.array(current_small.convert('L'))
                
                # 差分計算 (MAE: Mean Absolute Error)
                diff = np.mean(np.abs(self.last_screen_array.astype(int) - current_array.astype(int)))
                
                # 閾値設定 (経験則: 5.0以上で何らかの有意な変化)
                # 微細な変化（時計の変化など）は無視したい
                THRESHOLD = 15.0 
                
                if diff > THRESHOLD:
                    print(f"Screen change detected: diff={diff:.2f}")
                    
                    # 変化が落ち着くまで少し待つ（アニメーション完了待ち）
                    time.sleep(1.0)
                    
                    # 再度チェックして、まだ変化している最中か確認してもよいが、ここは即反応
                    
                    # AIに問い合わせ
                    # NOTE: メインスレッドの処理と競合しないように注意が必要だが、
                    # process_question は Thread でUIから呼ばれる設計になっている。
                    # ここからも呼び出してよい。
                    
                    # 「画面が変化しました。次は何をすればいいですか？」
                    next_question = "画面が変化しました。次の手順を教えてください。"
                    
                    # UIスレッドを経由せずに直接Controllerメソッドを呼ぶ
                    # ただし、UIへのアクセスがあるので注意。tkスレッドではないスレッドからのアクセス。
                    # ui_1120_01.py のメソッドは一部 tkinter のスレッドセーフティに依存するが、
                    # 基本的に after などを介さないと危険。
                    # しかし今回は簡易実装として直接呼び出す（多くのTkinter操作は許容される場合が多いが、add_messageなどは微妙）
                    # 本来は self.ui.root.after(...) を使うべき。
                    
                    # ひとひとまず非同期で実行
                    # フラグを一時的に落として連打防止
                    self.is_navigating = False 
                    
                    # NOTE: メインスレッド(root.after)で実行するとAPI待ち時間にUIが固まるため、
                    # 新しいスレッドで実行する。process_questionは元々スレッドセーフ（UI操作含む）に作られている前提。
                    threading.Thread(target=self.process_question, args=(next_question,), daemon=True).start()
                    
            except Exception as e:
                print(f"Navigation Loop Error: {e}")
                


    def on_speech_recognized(self, text):
        """音声認識コールバック"""
        if text:
            self.ui.set_input_text(text)
            self.ui.set_status("音声認識完了", "green")
            # 自動的に質問を送信
            time.sleep(0.05) # レスポンス短縮
            self.process_question(text)

    def handle_voice_input(self):
        """音声入力を処理"""
        try:
            self.ui.set_status("音声入力中...", "blue")
            
            # 音声認識（一度だけ実行）
            # 別スレッドで実行してUIをブロックしないようにする
            threading.Thread(target=self._run_voice_recognition, daemon=True).start()
        
        except Exception as e:
            error_msg = f"音声入力エラー: {str(e)}"
            print(error_msg)
            self.ui.set_status(error_msg, "red")

    def _run_voice_recognition(self):
        """音声認識を別スレッドで実行"""
        try:
            recognized_text = self.speech_module.recognize_once()
            
            if recognized_text:
                # コールバックはSpeechModule内で呼ばれるか、ここで直接処理する
                # SpeechModuleのrecognize_onceはコールバックを呼ばないのでここで呼ぶ
                self.on_speech_recognized(recognized_text)
            else:
                self.ui.set_status("音声を認識できませんでした", "red")
        except Exception as e:
            print(f"音声認識スレッドエラー: {e}")
            self.ui.set_status("音声認識エラー", "red")    
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
    controller = SENPAI_Controller()
    controller.run()

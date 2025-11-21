"""
UI Module for SENPAI Assistant
シンプルなAIアシスタントUI（矢印表示機能なし）
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class AssistantUI:
    def __init__(self, on_screenshot_callback, on_question_callback, on_voice_input_callback, on_tts_toggle_callback):
        """
        UIの初期化
        
        Args:
            on_screenshot_callback: スクリーンショットボタンのコールバック
            on_question_callback: 質問送信のコールバック
            on_voice_input_callback: 音声入力のコールバック
            on_tts_toggle_callback: TTS ON/OFFのコールバック
        """
        self.on_screenshot = on_screenshot_callback
        self.on_question = on_question_callback
        self.on_voice_input = on_voice_input_callback
        self.on_tts_toggle = on_tts_toggle_callback
        
        self.root = tk.Tk()
        self.root.title("SENPAI - AI Assistant")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.tts_enabled = tk.BooleanVar(value=True)
        self.is_recording = False
        
        self._create_widgets()
        
    def _create_widgets(self):
        """ウィジェットの作成"""
        
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # トップバー（ボタンエリア）
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # スクリーンショットボタン
        self.screenshot_btn = ttk.Button(
            top_frame,
            text="📸 スクリーンショット",
            command=self._on_screenshot_click
        )
        self.screenshot_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # TTS ON/OFFトグル
        self.tts_check = ttk.Checkbutton(
            top_frame,
            text="🔊 音声回答",
            variable=self.tts_enabled,
            command=self._on_tts_toggle
        )
        self.tts_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # ステータスラベル
        self.status_label = ttk.Label(top_frame, text="準備完了", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # 会話履歴エリア
        history_frame = ttk.Frame(main_frame)
        history_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            font=("Yu Gothic UI", 10),
            state=tk.DISABLED,
            background="#f5f5f5"
        )
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # テキストタグの設定
        self.history_text.tag_config("user", foreground="#0066cc", font=("Yu Gothic UI", 10, "bold"))
        self.history_text.tag_config("assistant", foreground="#333333", font=("Yu Gothic UI", 10))
        self.history_text.tag_config("timestamp", foreground="#999999", font=("Yu Gothic UI", 8))
        
        # 入力エリア
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        # 入力欄とマイクボタンを含むフレーム
        entry_container = ttk.Frame(input_frame)
        entry_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        entry_container.columnconfigure(0, weight=1)
        
        # テキスト入力欄
        self.input_entry = ttk.Entry(
            entry_container,
            font=("Yu Gothic UI", 11)
        )
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_entry.bind("<Return>", self._on_return_key)
        
        # マイクボタン（入力欄の右側）
        self.mic_btn = ttk.Button(
            entry_container,
            text="🎤",
            width=3,
            command=self._on_mic_click
        )
        self.mic_btn.grid(row=0, column=1)
        
        # プレースホルダー効果
        self.placeholder_text = "質問を入力してください（Returnキーで送信）"
        self._set_placeholder()
        self.input_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.input_entry.bind("<FocusOut>", self._on_entry_focus_out)
        
    def _set_placeholder(self):
        """プレースホルダーを設定"""
        self.input_entry.insert(0, self.placeholder_text)
        self.input_entry.config(foreground="gray")
    
    def _on_entry_focus_in(self, event):
        """入力欄フォーカス時"""
        if self.input_entry.get() == self.placeholder_text:
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(foreground="black")
    
    def _on_entry_focus_out(self, event):
        """入力欄フォーカス外れ時"""
        if not self.input_entry.get():
            self._set_placeholder()
    
    def _on_return_key(self, event):
        """Returnキー押下時"""
        self._on_question_submit()
    
    def _on_screenshot_click(self):
        """スクリーンショットボタンクリック"""
        self.set_status("スクリーンショット撮影中...", "blue")
        threading.Thread(target=self.on_screenshot, daemon=True).start()
    
    def _on_question_submit(self):
        """質問送信"""
        question = self.input_entry.get()
        
        # プレースホルダーまたは空の場合は何もしない
        if not question or question == self.placeholder_text:
            return
        
        # 入力欄をクリア
        self.input_entry.delete(0, tk.END)
        
        # コールバック実行
        self.set_status("AI分析中...", "blue")
        threading.Thread(target=self.on_question, args=(question,), daemon=True).start()
    
    def _on_mic_click(self):
        """マイクボタンクリック"""
        if self.is_recording:
            self.is_recording = False
            self.mic_btn.config(text="🎤")
            self.set_status("音声認識中...", "blue")
        else:
            self.is_recording = True
            self.mic_btn.config(text="⏹️")
            self.set_status("録音中...", "red")
        
        threading.Thread(target=self.on_voice_input, daemon=True).start()
    
    def _on_tts_toggle(self):
        """TTS ON/OFFトグル"""
        self.on_tts_toggle(self.tts_enabled.get())
    
    def add_message(self, role, message, timestamp=None):
        """
        メッセージを履歴に追加
        
        Args:
            role: "user" または "assistant"
            message: メッセージ内容
            timestamp: タイムスタンプ（オプション）
        """
        self.history_text.config(state=tk.NORMAL)
        
        # タイムスタンプ
        if timestamp:
            self.history_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # ロール名
        if role == "user":
            self.history_text.insert(tk.END, "あなた: ", "user")
        else:
            self.history_text.insert(tk.END, "SENPAI: ", "assistant")
        
        # メッセージ
        self.history_text.insert(tk.END, f"{message}\n\n", role)
        
        # 自動スクロール
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def set_status(self, message, color="black"):
        """ステータスメッセージを設定"""
        self.status_label.config(text=message, foreground=color)
    
    def set_input_text(self, text):
        """入力欄にテキストを設定"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, text)
        self.input_entry.config(foreground="black")
    
    def run(self):
        """UIメインループを開始"""
        self.root.mainloop()
    
    def close(self):
        """ウィンドウを閉じる"""
        self.root.quit()
        self.root.destroy()


# テスト用
if __name__ == "__main__":
    def test_screenshot():
        print("スクリーンショット撮影")
        import time
        time.sleep(1)
        ui.set_status("スクリーンショット完了", "green")
    
    def test_question(question):
        print(f"質問: {question}")
        import time
        time.sleep(2)
        ui.add_message("assistant", "これはテスト回答です。実際のAI回答がここに表示されます。")
        ui.set_status("準備完了", "green")
    
    def test_voice():
        print("音声入力")
        import time
        time.sleep(2)
        ui.set_input_text("これは音声入力のテストです")
        ui.set_status("準備完了", "green")
    
    def test_tts_toggle(enabled):
        print(f"TTS: {enabled}")
    
    ui = AssistantUI(test_screenshot, test_question, test_voice, test_tts_toggle)
    ui.add_message("assistant", "こんにちは！SENPAIです。画面を見て質問に答えます。")
    ui.run()


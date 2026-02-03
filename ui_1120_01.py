"""
UI Module for SENP_AI (Version 1120_01)
モデル選択機能付きUIモジュール
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class SENPAI_UI:
    def __init__(self, available_models, on_question_callback, 
                 on_voice_input_callback, on_tts_toggle_callback, on_model_change_callback):
        """
        UIの初期化
        
        Args:
            available_models: 利用可能なモデルのリスト [(id, name), ...]

            on_question_callback: 質問送信のコールバック
            on_voice_input_callback: 音声入力のコールバック
            on_tts_toggle_callback: TTS ON/OFFのコールバック
            on_model_change_callback: モデル変更のコールバック
        """
        self.available_models = available_models

        self.on_question = on_question_callback
        self.on_voice_input = on_voice_input_callback
        self.on_tts_toggle = on_tts_toggle_callback
        self.on_model_change = on_model_change_callback
        
        self.root = tk.Tk()
        self.root.title("SENP_AI - AI Assistant")
        
        # 画面サイズを取得して30%のサイズを計算
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.3)
        
        # ウィンドウサイズと位置を設定（画面中央に配置）
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # リサイズ可能にする
        self.root.resizable(True, True)
        
        # 最小サイズを調整（必要に応じて）
        # 最小サイズを調整（必要に応じて）
        # self.root.minsize(400, 300)
        self.root.minsize(10, 10) # 自由に縮小できるように最小サイズを小さく設定
        
        self.tts_enabled = tk.BooleanVar(value=True)
        self.selected_model = tk.StringVar(value=available_models[0][0])
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
        
        # 左側のボタングループ
        left_buttons = ttk.Frame(top_frame)
        left_buttons.pack(side=tk.LEFT)
        

        # TTS ON/OFFトグル
        self.tts_check = ttk.Checkbutton(
            left_buttons,
            text="🔊 音声回答",
            variable=self.tts_enabled,
            command=self._on_tts_toggle
        )
        self.tts_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # モデル選択
        model_frame = ttk.Frame(left_buttons)
        model_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(model_frame, text="🤖 モデル:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.selected_model,
            values=[f"{name}" for _, name in self.available_models],
            state="readonly",
            width=30
        )
        self.model_combo.pack(side=tk.LEFT)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_change)
        
        # 右側のステータス
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
        self.history_text.tag_config("model", foreground="#666666", font=("Yu Gothic UI", 8, "italic"))
        
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
    
    def _on_model_change(self, event):
        """モデル変更"""
        selected_index = self.model_combo.current()
        model_id = self.available_models[selected_index][0]
        self.on_model_change(model_id)
    
    def add_message(self, role, message, timestamp=None, model=None):
        """
        メッセージを履歴に追加
        
        Args:
            role: "user" または "assistant"
            message: メッセージ内容
            timestamp: タイムスタンプ（オプション）
            model: 使用したモデル名（assistantの場合のみ）
        """
        self.history_text.config(state=tk.NORMAL)
        
        # タイムスタンプ
        if timestamp:
            self.history_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # ロール名
        if role == "user":
            self.history_text.insert(tk.END, "あなた: ", "user")
        else:
            self.history_text.insert(tk.END, "SENP_AI: ", "assistant")
        
        # メッセージ
        self.history_text.insert(tk.END, f"{message}", role)
        
        # モデル名（assistantの場合）
        if role == "assistant" and model:
            self.history_text.insert(tk.END, f" (使用モデル: {model})", "model")
        
        self.history_text.insert(tk.END, "\n\n")
        
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

    def hide_window(self):
        """ウィンドウを非表示にする"""
        self.root.withdraw()

    def show_window(self):
        """ウィンドウを表示する"""
        self.root.deiconify()


# テスト用
if __name__ == "__main__":
    test_models = [
        ("gpt-5.1-instant", "GPT-5.1 Instant ⚡ (最新・推奨)"),
        ("gpt-4o-mini", "GPT-4o Mini (高速・低コスト)"),
    ]
    
    def test_screenshot():
        print("スクリーンショット撮影")
    
    def test_question(question):
        print(f"質問: {question}")
    
    def test_voice():
        print("音声入力")
    
    def test_tts_toggle(enabled):
        print(f"TTS: {enabled}")
    
    def test_model_change(model):
        print(f"モデル変更: {model}")
    
    ui = SENPAI_UI(test_models, test_screenshot, test_question, test_voice, test_tts_toggle, test_model_change)
    ui.add_message("assistant", "こんにちは！SENP_AIです。画面を見て質問に答えます。")
    ui.run()


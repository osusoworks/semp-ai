"""
UI Module for SENP_AI (Version 1120_01)
モデル選択機能付きUIモジュール - CustomTkinter Modern Design
"""

import tkinter as tk
from tkinter import font
import customtkinter as ctk
import threading

# CustomTkinterの設定
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class SENPAI_UI:
    def __init__(self, available_models, on_question_callback, 
                 on_voice_input_callback, on_tts_toggle_callback, on_model_change_callback):
        """
        UIの初期化
        """
        self.available_models = available_models
        self.on_question = on_question_callback
        self.on_voice_input = on_voice_input_callback
        self.on_tts_toggle = on_tts_toggle_callback
        self.on_model_change = on_model_change_callback
        
        # メインウィンドウの設定
        self.root = ctk.CTk()
        self.root.title("SENP_AI - AI Assistant")
        
        # 画面サイズを取得して30%のサイズを計算
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = int(screen_width * 0.25)
        window_height = int(screen_height * 0.35)
        
        # ウィンドウサイズと位置を設定（画面中央に配置）
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.minsize(300, 400) # 最小サイズを小さく設定
        self.root.resizable(True, True) # リサイズ許可
        
        # 変数初期化
        self.tts_enabled = tk.BooleanVar(value=True)
        # コンボボックス用の変数は文字列そのものを保持
        self.selected_model_id = available_models[0][0] 
        self.is_recording = False
        
        self._create_widgets()
        
    def _create_widgets(self):
        """モダンなウィジェットの作成"""
        
        # メインコンテナ（パディング用）
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) # 履歴エリアを伸縮
        
        # 1. ヘッダーエリア（ボタン類）
        header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        # モデル選択
        self.models_dict = {name: id for id, name in self.available_models}
        model_names = [name for _, name in self.available_models]
        
        self.model_combo = ctk.CTkComboBox(
            header_frame,
            values=model_names,
            command=self._on_model_change,
            width=250,
            font=("Yu Gothic UI", 12)
        )
        self.model_combo.pack(side="left", padx=(0, 10))
        # 初期値設定
        self.model_combo.set(model_names[0])
        
        # TTSスイッチ
        self.tts_switch = ctk.CTkSwitch(
            header_frame,
            text="音声回答",
            command=self._on_tts_toggle,
            variable=self.tts_enabled,
            onvalue=True,
            offvalue=False,
            font=("Yu Gothic UI", 12)
        )
        self.tts_switch.pack(side="left", padx=10)
        
        # ステータスラベル（右寄せ）
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="準備完了",
            text_color="gray",
            font=("Yu Gothic UI", 11)
        )
        self.status_label.pack(side="right")
        
        # 2. チャット履歴エリア
        # NOTE: 色分け(tag)機能のため、CTkTextboxではなく標準Textをカスタマイズして使う
        # テーマに合わせて背景色などを調整
        
        bg_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkTextbox"]["fg_color"])
        text_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
        
        self.history_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.history_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(0, weight=1)
        
        self.history_text = tk.Text(
            self.history_frame,
            wrap=tk.WORD,
            font=("Yu Gothic UI", 11),
            bg=bg_color,
            fg=text_color,
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.history_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # スクロールバー
        scrollbar = ctk.CTkScrollbar(self.history_frame, command=self.history_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        # テキストタグ設定
        self.history_text.tag_config("user", foreground="#3B8ED0", font=("Yu Gothic UI", 11, "bold")) # Blue
        self.history_text.tag_config("assistant", foreground=text_color, font=("Yu Gothic UI", 11))
        self.history_text.tag_config("timestamp", foreground="gray", font=("Yu Gothic UI", 9))
        self.history_text.tag_config("model", foreground="gray", font=("Yu Gothic UI", 9, "italic"))
        self.history_text.tag_config("error", foreground="#E04F5F") # Red
        
        # 3. 入力エリア
        input_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="質問を入力してください...",
            height=40,
            font=("Yu Gothic UI", 12)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", self._on_return_key)
        
        # ボタンコンテナ
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")
        
        # マイクボタン
        self.mic_btn = ctk.CTkButton(
            btn_frame,
            text="🎤",
            width=40,
            height=40,
            command=self._on_mic_click,
            fg_color="#333333",
            hover_color="#555555"
        )
        self.mic_btn.pack(side="left", padx=(0, 5))
        
        # 送信ボタン
        self.send_btn = ctk.CTkButton(
            btn_frame,
            text="送信",
            width=60,
            height=40,
            command=self._on_question_submit
        )
        self.send_btn.pack(side="left")

    def _on_return_key(self, event):
        self._on_question_submit()
    
    def _on_question_submit(self):
        question = self.input_entry.get()
        if not question:
            return
            
        self.input_entry.delete(0, tk.END)
        self.set_status("AI分析中...", "#3B8ED0") # Blue
        threading.Thread(target=self.on_question, args=(question,), daemon=True).start()
    
    def _on_mic_click(self):
        if self.is_recording:
            self.is_recording = False
            self.mic_btn.configure(text="🎤", fg_color="#333333")
            self.set_status("音声認識完了", "#2CC985") # Green
        else:
            self.is_recording = True
            self.mic_btn.configure(text="⏹️", fg_color="#E04F5F") # Red
            self.set_status("聞いています...", "#E04F5F")
        
        threading.Thread(target=self.on_voice_input, daemon=True).start()

    def _on_tts_toggle(self):
        # Switchの値がすでに変わっている
        self.on_tts_toggle(self.tts_enabled.get())

    def _on_model_change(self, selected_name):
        # 名前からIDを逆引き
        model_id = self.models_dict.get(selected_name)
        if model_id:
            self.on_model_change(model_id)

    def add_message(self, role, message, timestamp=None, model=None):
        self.history_text.config(state=tk.NORMAL)
        
        if timestamp:
            self.history_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        if role == "user":
            self.history_text.insert(tk.END, "あなた: ", "user")
        else:
            self.history_text.insert(tk.END, "SENP_AI: ", "assistant")
            
        self.history_text.insert(tk.END, f"{message}", role if role != "assistant" else "assistant")
        
        if role == "assistant" and model:
            self.history_text.insert(tk.END, f" ({model})", "model")
            
        self.history_text.insert(tk.END, "\n\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def set_status(self, message, color="gray"):
        # CustomTkinterは色名ではなくHEX推奨だが、tkinterの色名も大体通る
        # color引数が "red" などの場合、モダンな色に置き換える
        color_map = {
            "red": "#E04F5F",
            "green": "#2CC985",
            "blue": "#3B8ED0",
            "black": "gray", # 通常色
        }
        actual_color = color_map.get(color, color)
        self.status_label.configure(text=message, text_color=actual_color)

    def set_input_text(self, text):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, text)
    
    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.quit()
        self.root.destroy()
        
    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()

if __name__ == "__main__":
    # Test logic
    test_models = [("gemini-pro", "Gemini Pro"), ("gemini-flash", "Gemini Flash")]
    app = SENPAI_UI(test_models, lambda x: print(x), lambda: print("mic"), lambda x: print(x), lambda x: print(x))
    app.add_message("user", "Hello", "12:00")
    app.add_message("assistant", "Hi there!", "12:01", "gemini-pro")
    app.run()

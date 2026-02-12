"""
UI Module for SENP_AI (Version 1120_01)
モデル選択機能付きUIモジュール - CustomTkinter Modern Design
"""

import tkinter as tk
from tkinter import font
import customtkinter as ctk
import threading
import os
import shutil
from PIL import Image

# CustomTkinterの設定
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, available_models, current_model, tts_enabled, 
                 on_update_settings, on_model_change, on_tts_toggle):
        super().__init__(parent)
        self.title("設定")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.parent = parent
        self.on_update_settings = on_update_settings
        self.on_model_change = on_model_change
        self.on_tts_toggle = on_tts_toggle
        
        # Keep window on top transiently or just normal
        self.transient(parent)
        self.grab_set() # Modal behavior
        
        # Variables
        self.var_tts = tk.BooleanVar(value=tts_enabled)
        self.var_ontop = tk.BooleanVar(value=parent.attributes("-topmost"))
        self.var_opacity = tk.DoubleVar(value=parent.attributes("-alpha"))
        # Font size for history
        current_font = parent.history_font_size if hasattr(parent, 'history_font_size') else 11
        self.var_font_size = tk.IntVar(value=current_font)
        
        self.models_dict = {name: id for id, name in available_models}
        current_model_name = next((name for id, name in available_models if id == current_model), available_models[0][1])
        self.var_model = tk.StringVar(value=current_model_name)
        
        self._create_widgets()
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tabview.add("一般")
        self.tabview.add("表示")
        self.tabview.add("AI・音声")
        
        # --- General Tab ---
        gen_frame = self.tabview.tab("一般")
        gen_frame.grid_columnconfigure(0, weight=1)
        
        # Appearance Mode
        lbl_mode = ctk.CTkLabel(gen_frame, text="外観モード:", anchor="w")
        lbl_mode.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        self.option_mode = ctk.CTkOptionMenu(gen_frame, values=["System", "Light", "Dark"],
                                           command=self._change_appearance_mode)
        self.option_mode.set(ctk.get_appearance_mode())
        self.option_mode.grid(row=1, column=0, padx=10, pady=(5,15), sticky="ew")

        # Color Theme
        lbl_color = ctk.CTkLabel(gen_frame, text="アクセントカラー (再起動推奨):", anchor="w")
        lbl_color.grid(row=2, column=0, padx=10, pady=(10,0), sticky="ew")
        self.option_color = ctk.CTkOptionMenu(gen_frame, values=["blue", "green", "dark-blue"],
                                            command=self._change_color_theme)
        self.option_color.set(ctk.ThemeManager.active_theme_name if hasattr(ctk.ThemeManager, 'active_theme_name') else "blue")
        self.option_color.grid(row=3, column=0, padx=10, pady=(5,15), sticky="ew")
        
        # --- Display Tab ---
        disp_frame = self.tabview.tab("表示")
        disp_frame.grid_columnconfigure(0, weight=1)
        
        # Always on Top
        self.switch_ontop = ctk.CTkSwitch(disp_frame, text="常に手前に表示", variable=self.var_ontop, command=self._update_ontop)
        self.switch_ontop.grid(row=0, column=0, padx=10, pady=(15,10), sticky="w")
        
        # Opacity
        lbl_opacity = ctk.CTkLabel(disp_frame, text="ウィンドウの不透明度:", anchor="w")
        lbl_opacity.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")
        self.slider_opacity = ctk.CTkSlider(disp_frame, from_=0.3, to=1.0, variable=self.var_opacity, command=self._update_opacity)
        self.slider_opacity.grid(row=2, column=0, padx=10, pady=(5,15), sticky="ew")
        
        # Font Size
        lbl_font = ctk.CTkLabel(disp_frame, text=f"フォントサイズ: {self.var_font_size.get()}", anchor="w")
        lbl_font.grid(row=3, column=0, padx=10, pady=(10,0), sticky="ew")
        
        def update_font_label(value):
            lbl_font.configure(text=f"フォントサイズ: {int(value)}")
            self._update_font_size(int(value))
            
        self.slider_font = ctk.CTkSlider(disp_frame, from_=8, to=24, number_of_steps=16, variable=self.var_font_size, command=update_font_label)
        self.slider_font.grid(row=4, column=0, padx=10, pady=(5,15), sticky="ew")
        
        # --- AI & Voice Tab ---
        ai_frame = self.tabview.tab("AI・音声")
        ai_frame.grid_columnconfigure(0, weight=1)
        
        # Model
        lbl_model = ctk.CTkLabel(ai_frame, text="AIモデル:", anchor="w")
        lbl_model.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        self.option_model = ctk.CTkOptionMenu(ai_frame, values=list(self.models_dict.keys()),
                                            variable=self.var_model,
                                            command=self._on_model_select)
        self.option_model.grid(row=1, column=0, padx=10, pady=(5,15), sticky="ew")
        
        # TTS
        self.switch_tts = ctk.CTkSwitch(ai_frame, text="音声読み上げ (TTS)", variable=self.var_tts, command=self._on_tts_switch)
        self.switch_tts.grid(row=2, column=0, padx=10, pady=(15,10), sticky="w")
        
    def _change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def _change_color_theme(self, new_color_theme):
        ctk.set_default_color_theme(new_color_theme)
        # Note: Changing color theme at runtime might not update everything perfectly without restart/redraw
        
    def _update_ontop(self):
        self.parent.attributes("-topmost", self.var_ontop.get())
        
    def _update_opacity(self, value):
        self.parent.attributes("-alpha", value)
        
    def _update_font_size(self, value):
        self.on_update_settings("font_size", value)
        
    def _on_model_select(self, choice):
        model_id = self.models_dict.get(choice)
        if model_id:
            self.on_model_change(model_id)
            
    def _on_tts_switch(self):
        self.on_tts_toggle(self.var_tts.get())

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
        
        self.history_font_size = 11 # Default font size
        
        # 歯車アイコン読み込み
        self.gear_image = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(current_dir, "assets")
        gear_icon_path = os.path.join(assets_dir, "gear_icon_white.png")
        if os.path.exists(gear_icon_path):
            try:
                pil_img = Image.open(gear_icon_path)
                self.gear_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(20, 20))
            except:
                pass
        
        # 音声入力ボタンの画像設定
        self.mic_image = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(current_dir, "assets")
        mic_icon_path = os.path.join(assets_dir, "mic_icon_white.png")
        
        if os.path.exists(mic_icon_path):
            try:
                pil_image = Image.open(mic_icon_path)
                # ボタンがdark(#333333)なので、アイコンは常に白(light_imageとdark_image両方に白画像を指定)
                self.mic_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(24, 24))
            except Exception as e:
                print(f"Failed to load image: {e}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """モダンなウィジェットの作成"""
        
        # メインコンテナ（パディング用）
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) # 履歴エリアを伸縮
        
        # 1. ヘッダーエリア（ボタン類）
        header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1) # Spacer
        
        # ステータスラベル（左側）
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="準備完了",
            text_color="gray",
            font=("Yu Gothic UI", 11)
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # 設定ボタン（右側）
        self.settings_btn = ctk.CTkButton(
            header_frame,
            text="" if self.gear_image else "⚙",
            image=self.gear_image,
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=("black", "white"),
            command=self._open_settings
        )
        self.settings_btn.grid(row=0, column=1, sticky="e")
        
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
            font=("Yu Gothic UI", self.history_font_size),
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
        self._update_text_tags()
        
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
            text="" if self.mic_image else "🎤",
            image=self.mic_image,
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
            if self.mic_image:
                self.mic_btn.configure(text="", image=self.mic_image, fg_color="#333333")
            else:
                self.mic_btn.configure(text="🎤", fg_color="#333333")
            self.set_status("音声認識完了", "#2CC985") # Green
        else:
            self.is_recording = True
            # 録音中は停止アイコン（テキスト）を表示
            self.mic_btn.configure(text="⏹️", image=None, fg_color="#E04F5F") # Red
            self.set_status("聞いています...", "#E04F5F")
        
        threading.Thread(target=self.on_voice_input, daemon=True).start()

    def _open_settings(self):
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
            
        self.settings_window = SettingsWindow(
            self.root,
            self.available_models,
            self.selected_model_id,
            self.tts_enabled.get(),
            self._handle_setting_update,
            self.on_model_change,
            self.on_tts_toggle
        )
        
    def _handle_setting_update(self, key, value):
        if key == "font_size":
            self.history_font_size = value
            self.history_text.configure(font=("Yu Gothic UI", self.history_font_size))
            self._update_text_tags()
    
    def _update_text_tags(self):
        text_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
        base_size = self.history_font_size
        
        self.history_text.tag_config("user", foreground="#3B8ED0", font=("Yu Gothic UI", base_size, "bold"))
        self.history_text.tag_config("assistant", foreground=text_color, font=("Yu Gothic UI", base_size))
        # Timestamp/Model info slightly smaller
        small_size = max(8, base_size - 2)
        self.history_text.tag_config("timestamp", foreground="gray", font=("Yu Gothic UI", small_size))
        self.history_text.tag_config("model", foreground="gray", font=("Yu Gothic UI", small_size, "italic"))
        self.history_text.tag_config("error", foreground="#E04F5F", font=("Yu Gothic UI", base_size))

    def _on_tts_toggle(self, enabled): # Update signature to match usage
        self.tts_enabled.set(enabled)
        self.on_tts_toggle(enabled)

    def _on_model_change(self, model_id): # Update signature
        self.selected_model_id = model_id
        self.on_model_change(model_id)
        # Update settings window state if open
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
             pass # Logic is handled by sharing vars or callbacks, simplified here

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

    def show_tutorial_arrow(self, target_widget=None):
        """
        （旧メソッド互換用：内部ウィジェット向け）
        """
        # 以前の実装をそのまま使うか、または削除してもよいが、
        # 今回はオーバーレイ版を優先するため、呼び出し側で使い分ける。
        pass

    def show_global_arrow(self, x, y):
        """
        画面上の指定座標(x, y)に赤い矢印を表示する（透明ウィンドウを使用）
        """
        # 既存の矢印があれば消す
        self.hide_tutorial_arrow()
        
        # オーバーレイウィンドウ作成
        self.overlay_window = tk.Toplevel(self.root)
        
        # ウィンドウ装飾なし
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes("-topmost", True)
        
        # 透明化設定（Windows用）
        # 特定の色を透明色として指定
        transparent_color = "#000001" # ほぼ黒だが使われない色
        self.overlay_window.attributes("-transparentcolor", transparent_color)
        self.overlay_window.config(bg=transparent_color)
        
        # 矢印サイズ
        arrow_w = 40
        arrow_h = 60
        
        # キャンバスサイズ（矢印が動く範囲を確保）
        canvas_w = arrow_w
        canvas_h = arrow_h + 20 # アニメーション分
        
        # ウィンドウ位置設定 (矢印の先端が x, y に来るように配置)
        # 矢印の形状: Tip=(w/2, h) -> 下向き
        # ウィンドウの左上座標 (wx, wy)
        # Tip座標 in canvas: (w/2, h + anim_offset)
        # Screen (x, y) = (wx + w/2, wy + h + anim_offset)
        # wy = y - h - anim_offset
        # wx = x - w/2
        
        # アニメーション初期オフセット
        self.arrow_anim_offset = 0
        
        base_wx = int(x - (canvas_w / 2))
        base_wy = int(y - canvas_h)
        
        self.overlay_window.geometry(f"{canvas_w}x{canvas_h}+{base_wx}+{base_wy}")
        
        # キャンバス作成
        self.arrow_canvas = tk.Canvas(
            self.overlay_window,
            width=canvas_w,
            height=canvas_h,
            bg=transparent_color,
            highlightthickness=0,
            bd=0
        )
        self.arrow_canvas.pack()
        
        # 矢印描画 (キャンバス内座標)
        # Tip at (w/2, h)
        pointer_x = canvas_w / 2
        pointer_y = arrow_h # Tip position (bottom of arrow shape)
        
        points = [
            pointer_x, pointer_y,          # 先端
            0, pointer_y * 0.6,            # 左翼
            canvas_w * 0.3, pointer_y * 0.6,# 軸左付根
            canvas_w * 0.3, 0,            # 軸左上
            canvas_w * 0.7, 0,            # 軸右上
            canvas_w * 0.7, pointer_y * 0.6,# 軸右付根
            canvas_w, pointer_y * 0.6       # 右翼
        ]
        
        self.arrow_id = self.arrow_canvas.create_polygon(points, fill="#E04F5F", outline="#C03F4F", width=2)
        
        # イベントバインド
        self.overlay_window.bind("<Button-3>", self.hide_tutorial_arrow)
        self.arrow_canvas.bind("<Button-3>", self.hide_tutorial_arrow)
        
        # プロパティ保存
        self.arrow_base_y = 0 # Canvas内のY基準
        
        # アニメーション開始
        self.arrow_anim_direction = 1
        self._animate_overlay_arrow()
        
        # 3分後に自動消滅
        self.arrow_timeout = self.root.after(180000, self.hide_tutorial_arrow)

    def _animate_overlay_arrow(self):
        if not hasattr(self, 'overlay_window') or not self.overlay_window or not self.overlay_window.winfo_exists():
            return
            
        step = 1.0
        limit = 10
        
        self.arrow_anim_offset += step * self.arrow_anim_direction
        
        if self.arrow_anim_offset > limit:
            self.arrow_anim_direction = -1
        elif self.arrow_anim_offset < 0:
            self.arrow_anim_direction = 1
        
        # キャンバス内で矢印を移動
        # create_polygonの座標を更新するのは面倒なので、moveを使う
        # しかしmoveは相対移動。絶対位置計算が必要。
        # 毎回再描画するか、オフセットを管理して move(dx, dy) する
        
        # 前回との差分を計算して移動
        # 面倒なので coords で再設定
        arrow_w = 40
        arrow_h = 60
        canvas_w = arrow_w
        
        # Base Y + offset
        current_base_y = self.arrow_anim_offset
        
        pointer_x = canvas_w / 2
        pointer_y = arrow_h + current_base_y
        
        points = [
            pointer_x, pointer_y,
            0, pointer_y - (arrow_h * 0.4),
            canvas_w * 0.3, pointer_y - (arrow_h * 0.4),
            canvas_w * 0.3, current_base_y,
            canvas_w * 0.7, current_base_y,
            canvas_w * 0.7, pointer_y - (arrow_h * 0.4),
            canvas_w, pointer_y - (arrow_h * 0.4)
        ]
        
        self.arrow_canvas.coords(self.arrow_id, *points)
        
        self.arrow_anim_id = self.root.after(50, self._animate_overlay_arrow)

    def hide_tutorial_arrow(self, event=None):
        """矢印を消す（オーバーレイも内部も）"""
        if hasattr(self, 'arrow_timeout') and self.arrow_timeout:
            self.root.after_cancel(self.arrow_timeout)
            self.arrow_timeout = None
            
        if hasattr(self, 'arrow_anim_id') and self.arrow_anim_id:
            self.root.after_cancel(self.arrow_anim_id)
            self.arrow_anim_id = None
            
        # 内部矢印削除
        if hasattr(self, 'arrow_canvas') and self.arrow_canvas:
            try:
                self.arrow_canvas.destroy()
            except:
                pass
            self.arrow_canvas = None
            
        # オーバーレイ削除
        if hasattr(self, 'overlay_window') and self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
            self.overlay_window = None

if __name__ == "__main__":
    # Test logic
    test_models = [("gemini-pro", "Gemini Pro"), ("gemini-flash", "Gemini Flash")]
    app = SENPAI_UI(test_models, lambda x: print(x), lambda: print("mic"), lambda x: print(x), lambda x: print(x))
    app.add_message("user", "Hello", "12:00")
    app.add_message("assistant", "Hi there!", "12:01", "gemini-pro")
    app.run()

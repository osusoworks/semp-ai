@echo off
chcp 65001
echo 必要なパッケージをインストールしています...
pip install customtkinter google-generativeai Pillow SpeechRecognition gTTS pygame requests

echo.
echo アプリケーションを起動します...
python run.py
pause

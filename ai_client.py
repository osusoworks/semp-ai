
import os
import requests

class RemoteAIModule:
    """
    Cloud Run上のバックエンドAIサービスを利用するクライアントモジュール
    ローカルのAIModuleと互換性のあるインターフェースを提供します
    """
    def __init__(self, backend_url=None):
        url = backend_url or os.environ.get("SENP_AI_BACKEND_URL")
        
        if url:
            # 誤ってプロトコルが重複している場合（https://https://...）を修正
            while url.startswith("https://https://"):
                url = url.replace("https://https://", "https://")
            while url.startswith("http://http://"):
                url = url.replace("http://http://", "http://")
            
            # 末尾のスラッシュを削除して、パス結合時のエラーを防ぐ
            url = url.rstrip("/")
            
            self.backend_url = url
            print(f"Cloud AI Client initialized with URL: {self.backend_url}")
        else:
            self.backend_url = "http://localhost:8080"
            print(f"Cloud AI Client initialized with default URL: {self.backend_url}")
            
        self.current_model = "gemini-3.0-flash" # デフォルトモデル

    def set_model(self, model):
        """
        使用するモデルを設定
        """
        self.current_model = model
        print(f"Remote model selected: {self.current_model}")

    def get_model(self):
        return self.current_model

    @staticmethod
    def get_available_models():
        """UIで選択可能なモデルリストを返す"""
        return [
            ("gemini-3.0-flash", "Gemini 3 Flash (最新・最高速)"),
            ("gemini-3.0-pro", "Gemini 3 Pro (最新・最高精度)"),
            ("gemini-2.0-flash", "Gemini 2.0 Flash (安定・高速)"),
            ("gemini-2.0-pro", "Gemini 2.0 Pro (高性能)"),
            ("gemini-1.5-flash", "Gemini 1.5 Flash (軽量版)"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro (旧世代・高精度)"),
        ]

    def analyze_screen(self, screenshot_path, user_question):
        """
        スクリーンショットをバックエンドに送信して分析
        """
        if not self.backend_url:
            return {"success": False, "error": "Backend URL not configured"}

        try:
            files = []
            # パスのリストか単一パスかを判定
            paths = screenshot_path if isinstance(screenshot_path, list) else [screenshot_path]
            
            # ファイルを開いてリストに追加
            opened_files = []
            for path in paths:
                try:
                    f = open(path, 'rb')
                    opened_files.append(f)
                    # keyを 'images' にして複数送信対応
                    files.append(('images', (os.path.basename(path), f, 'image/png')))
                except Exception as e:
                    print(f"Error opening file {path}: {e}")

            # モデル情報を含める
            data = {
                'question': user_question,
                'model': self.current_model
            }
            
            # リクエスト送信
            target_url = f"{self.backend_url}/analyze"
            print(f"Sending request to: {target_url} (Model: {self.current_model})")
            response = requests.post(target_url, data=data, files=files)
            
            # ファイルを閉じる
            for f in opened_files:
                f.close()
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                error_msg = f"Server Error ({response.status_code}): {response.text}"
                print(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Connection Error: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}

# テスト用
if __name__ == "__main__":
    client = RemoteAIModule()

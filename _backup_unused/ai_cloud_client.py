
import os
import requests

class RemoteAIModule:
    """
    Cloud Run上のバックエンドAIサービスを利用するクライアントモジュール
    ローカルのAIModuleと互換性のあるインターフェースを提供します
    """
    def __init__(self, backend_url=None):
        self.backend_url = backend_url or os.environ.get("SENP_AI_BACKEND_URL")
        # デフォルトでローカルテスト用のURLを設定（必要に応じて変更）
        if not self.backend_url:
            self.backend_url = "http://localhost:8080"
            print(f"Cloud AI Client initialized with default URL: {self.backend_url}")
        else:
            print(f"Cloud AI Client initialized with URL: {self.backend_url}")

    def set_model(self, model):
        # リモート側で制御するため、現在は何もしないがインターフェースとして残す
        print(f"Remote model setting check: {model}")
        pass

    def get_model(self):
        return "cloud-run-model"

<<<<<<< HEAD
    @staticmethod
    def get_available_models():
        """UI互換性のために利用可能なモデルリストを返す"""
        return [
            ("cloud-run-model", "Google Cloud Run (Gemini)"),
        ]

=======
>>>>>>> 6a513095656cc68912b8ce88637abe922d2b7a88
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

            data = {'question': user_question}
            
            # リクエスト送信
            target_url = f"{self.backend_url}/analyze"
            print(f"Sending request to: {target_url}")
            response = requests.post(target_url, data=data, files=files)
            
            # ファイルを閉じる
            for f in opened_files:
                f.close()
            
            if response.status_code == 200:
                result = response.json()
                # ローカル互換のために success フィールドなどを確認
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
    # 動作確認 (バックエンドが起動している前提)
    client = RemoteAIModule()
    # ダミー画像のパスなどを指定してテスト可能

import os
import shutil

files_to_move = [
    "ai_1120_01.py",
    "create_gear.py",
    "create_icon.py",
    "setup_assets.py",
    "perform_cleanup.py",
    "cleanup_log.txt",
    "install.sh",
    "setup_env.bat"
]

mapping = {
    "controller_1120_01.py": "controller.py",
    "ui_1120_01.py": "ui.py",
    "speech_1120_01.py": "speech.py",
    "tts_1120_01.py": "tts.py",
    "ai_cloud_client.py": "ai_client.py"
}

os.makedirs("_backup_unused", exist_ok=True)

for f in files_to_move:
    if os.path.exists(f):
        try:
            shutil.move(f, os.path.join("_backup_unused", f))
            print(f"Moved {f} to _backup_unused")
        except Exception as e:
            print(f"Failed to move {f}: {e}")

for old, new in mapping.items():
    if os.path.exists(old):
        try:
            os.rename(old, new)
            print(f"Renamed {old} to {new}")
        except Exception as e:
            print(f"Failed to rename {old}: {e}")

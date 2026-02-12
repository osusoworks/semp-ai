import os
import shutil

target_dir = os.path.join(os.getcwd(), 'assets')
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

source_file = r"C:\Users\sr44w\.gemini\antigravity\brain\5a51db41-3971-4336-9bf7-e5cccd3e390f\uploaded_media_1770115057520.png"
dest_file = os.path.join(target_dir, "mic_icon.png")

try:
    if os.path.exists(source_file):
        shutil.copy2(source_file, dest_file)
        with open(os.path.join(target_dir, "copy_done.txt"), "w") as f:
            f.write("Success")
    else:
        with open(os.path.join(target_dir, "copy_error.txt"), "w") as f:
            f.write(f"Source not found: {source_file}")
except Exception as e:
    with open(os.path.join(target_dir, "copy_exception.txt"), "w") as f:
        f.write(str(e))

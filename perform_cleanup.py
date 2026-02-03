import os
import shutil
import glob
import sys
import datetime

# Log function
def log(msg):
    with open("cleanup_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")
    print(msg)

KEEP_FILES = {
    'run.py',
    'controller_1120_01.py',
    'ui_1120_01.py',
    'ai_1120_01.py',
    'speech_1120_01.py',
    'tts_1120_01.py',
    'requirements.txt',
    'README.md',
    'PROJECT_STRUCTURE.md',
    'install.sh',
    'perform_cleanup.py',
    'cleanup_log.txt'
}

BACKUP_DIR = '_backup_unused'

def main():
    log("Starting cleanup script...")
    
    # Create backup dir
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
            log(f"Created directory: {BACKUP_DIR}")
        except Exception as e:
            log(f"Failed to create directory {BACKUP_DIR}: {e}")
            return
    else:
        log(f"Directory {BACKUP_DIR} already exists")

    # Get all files
    all_files = os.listdir('.')
    
    moved_count = 0
    
    for filename in all_files:
        if os.path.isdir(filename):
            continue
            
        if filename in KEEP_FILES:
            continue
            
        # Target only .py and .md files
        if filename.endswith('.py') or filename.endswith('.md'):
            src = filename
            dst = os.path.join(BACKUP_DIR, filename)
            
            try:
                shutil.move(src, dst)
                log(f"Moved: {filename}")
                moved_count += 1
            except Exception as e:
                log(f"Error moving {filename}: {e}")

    log(f"Cleanup complete. Moved {moved_count} files.")

if __name__ == "__main__":
    main()

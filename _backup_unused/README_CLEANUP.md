# Project Cleanup

This directory contains a cleanup script `perform_cleanup.py` designed to organize the project files.

## What it does

It moves files that are not part of the currently active "1120_01" version into a backup folder named `_backup_unused`.

## Files Kept (Active Project)

- `run.py`
- `controller_1120_01.py`
- `ui_1120_01.py`
- `ai_1120_01.py`
- `speech_1120_01.py`
- `tts_1120_01.py`
- `requirements.txt`
- `README.md`
- `install.sh`
- `PROJECT_STRUCTURE.md`

## How to run

Execute the following command in your terminal:

```bash
python perform_cleanup.py
```

If you are using the Python Launcher on Windows:

```bash
py perform_cleanup.py
```

Check `cleanup_log.txt` for details on what was moved.

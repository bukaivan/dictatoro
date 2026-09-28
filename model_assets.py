"""Resolve the read-only Base model shipped alongside the application."""
from pathlib import Path

BASE_FILES = ('config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt')


def bundled_base_path():
    folder = Path(__file__).resolve().parent / 'models' / 'base'
    if all((folder / name).is_file() and (folder / name).stat().st_size > 0 for name in BASE_FILES):
        return folder
    return None

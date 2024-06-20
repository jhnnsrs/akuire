import os
from pathlib import Path


def get_absolute_path(file_path: str) -> str:
    return Path(os.path.abspath(__file__)).parent / file_path

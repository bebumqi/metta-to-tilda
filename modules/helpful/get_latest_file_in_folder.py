import glob
import os
from pathlib import Path


def get_latest_file_in_folder(path: Path, file_name_mask='*') -> Path:
    list_of_files = glob.glob(os.path.join(path, file_name_mask))
    latest_file = max(list_of_files, key=os.path.getctime)
    return Path(latest_file)

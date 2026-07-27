import json
from pathlib import Path

import yaml


def parse_file(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()
    content = path.read_text()

    if extension == '.json':
        return json.loads(content)
    if extension in {'.yml', '.yaml'}:
        return yaml.safe_load(content)

    raise ValueError(f'Unsupported file format: {extension}')

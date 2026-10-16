
import json
import os
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIRS = {
    "text": PROJECT_ROOT / "data" / "processed" / "text",
    "tables": PROJECT_ROOT / "data" / "processed" / "tables",
    "charts": PROJECT_ROOT / "data" / "processed" / "charts",
    "metadata": PROJECT_ROOT / "data" / "processed" / "metadata",
}


def save_json(data: Any, category: str, filename: str) -> Path:
    """Persist structured artifacts as JSON using an atomic replacement."""

    if category not in PROCESSED_DIRS:
        raise ValueError(f"Unsupported artifact category: {category}")

    if Path(filename).name != filename or Path(filename).suffix.lower() != ".json":
        raise ValueError("filename must be a simple .json filename")

    output_dir = PROCESSED_DIRS[category]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_dir,
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(data, temp_file, ensure_ascii=False, indent=2)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(temp_path, output_path)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

    return output_path

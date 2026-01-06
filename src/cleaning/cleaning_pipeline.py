from pathlib import Path
import json


def get_latest_cleaned_file(cleaned_dir="data/cleaned"):
    cleaned_dir = Path(cleaned_dir)

    cleaned_files = list(cleaned_dir.glob("*_cleaned.json"))

    if not cleaned_files:
        raise FileNotFoundError(
            f"No cleaned JSON files found in {cleaned_dir}"
        )

    # Pick most recently modified file
    latest_file = max(cleaned_files, key=lambda f: f.stat().st_mtime)

    return str(latest_file)


def save_cleaned_pages(pages, output_path):
    """Save cleaned pages list to a JSON file at `output_path`.

    Returns the output path as a string.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    return str(output_path)
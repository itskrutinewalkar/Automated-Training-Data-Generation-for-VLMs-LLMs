from pathlib import Path

def get_latest_cleaned_file(cleaned_dir="data/cleaned"):
    cleaned_dir = Path(cleaned_dir)

    cleaned_files = list(cleaned_dir.glob("*_cleaned.json"))

    if not cleaned_files:
        raise FileNotFoundError(
            f"No cleaned JSON files found in {cleaned_dir}"
        )

    # Pick most recently modified file
    latest_file = max(cleaned_files, key=lambda f: f.stat().st_mtime)

    return latest_file
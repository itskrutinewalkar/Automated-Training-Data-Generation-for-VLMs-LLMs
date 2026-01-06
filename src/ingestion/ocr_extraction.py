# src/ingestion/ocr_extraction.py
import os
import json
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from pathlib import Path

def pdf_to_images(pdf_path, image_output_dir=None):
    pdf_path = Path(pdf_path)
    if image_output_dir is None:
        image_output_dir = Path("data/processed/images")
    else:
        image_output_dir = Path(image_output_dir)

    image_output_dir.mkdir(parents=True, exist_ok=True)

    pages = convert_from_path(str(pdf_path), dpi=300)
    image_paths = []

    for i, page in enumerate(pages):
        image_path = image_output_dir / f"page_{i+1}.jpg"
        page.save(image_path, "JPEG")
        image_paths.append(str(image_path))

    print(f"[INFO] {len(image_paths)} pages saved in {image_output_dir}")
    return image_paths

def extract_text_from_images(image_paths, ocr_output_path=None):
    if ocr_output_path is None:
        ocr_output_path = Path("../data/processed/ocr_output.json")
    else:
        ocr_output_path = Path(ocr_output_path)

    # Ensure directory exists
    ocr_output_path.parent.mkdir(parents=True, exist_ok=True)

    extracted_data = []
    for i, img_path in enumerate(image_paths):
        try:
            text = pytesseract.image_to_string(Image.open(img_path))
        except Exception as e:
            print(f"[ERROR] OCR failed for {img_path}: {e}")
            text = ""

        extracted_data.append({
            "page_number": i + 1,
            "image_path": img_path,
            "text": text.strip(),
            "raw_text": text.strip()
        })
        print(f"[INFO] Extracted text from page {i+1}")

    # Write OCR output
    with open(ocr_output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2)

    print(f"[INFO] OCR results saved to {ocr_output_path}")
    return extracted_data
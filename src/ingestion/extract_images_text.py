"""
extract_images_text.py

Uses Method C:
✔ Convert PDF → page images
✔ OCR the whole page
✔ Detect image regions using OpenCV
✔ Crop & save detected images
✔ Output JSON per page
"""

import os
import sys
import json
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import cv2
import numpy as np


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def pdf_to_page_images(pdf_path, pages_out_dir, dpi=300):
    """Converts each PDF page into a PNG image."""
    ensure_dir(pages_out_dir)
    pages = convert_from_path(pdf_path, dpi=dpi)
    page_paths = []
    base = Path(pdf_path).stem

    for i, page in enumerate(pages, start=1):
        out_path = Path(pages_out_dir) / f"{base}_page_{i}.png"
        page.save(out_path, "PNG")
        page_paths.append(str(out_path))

    return page_paths


def detect_images_opencv(page_image_path, crops_out_dir, prefix, min_area=5000):
    """
    Method C: Detect images using OpenCV (contours + morphology).
    Returns list of cropped image file paths.
    """
    ensure_dir(crops_out_dir)

    image = cv2.imread(page_image_path)
    if image is None:
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 1. Edge detection
    edges = cv2.Canny(gray, 100, 200)

    # 2. Dilate to merge close edges
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)

    # 3. Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    saved = []
    crop_count = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        
        # Filter small or too thin regions
        if area < min_area:
            continue
        if w < 50 or h < 50:
            continue

        # Extract ROI
        roi = image[y:y+h, x:x+w]
        crop_path = Path(crops_out_dir) / f"{prefix}_crop_{crop_count}.png"
        cv2.imwrite(str(crop_path), roi)
        saved.append(str(crop_path))
        crop_count += 1

    return saved


def ocr_text(page_image_path):
    try:
        text = pytesseract.image_to_string(Image.open(page_image_path))
        return text.replace("\n", " ").strip()
    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return ""


def process_pdf(pdf_path, base_output="data"):
    pdf_path = str(pdf_path)
    pdf_name = Path(pdf_path).stem

    # Directories
    pages_out_dir = Path(base_output) / "processed" / "pages"
    crops_out_dir = Path(base_output) / "processed" / "crops" / pdf_name
    json_out_dir  = Path(base_output) / "output" / "ocr_json"

    ensure_dir(pages_out_dir)
    ensure_dir(crops_out_dir)
    ensure_dir(json_out_dir)

    print(f"[INFO] Converting PDF to page images…")
    page_images = pdf_to_page_images(pdf_path, pages_out_dir)

    results = []

    for page_number, page_img in enumerate(page_images, start=1):
        print(f"\n[INFO] Processing page {page_number}…")
        
        # Detect images using OpenCV
        crops = detect_images_opencv(page_img, crops_out_dir, prefix=f"{pdf_name}_p{page_number}")

        print(f"[INFO] Found {len(crops)} image(s) on page {page_number}")

        # OCR full page
        text = ocr_text(page_img)

        results.append({
            "page_number": page_number,
            "page_image": page_img,
            "ocr_text": text,
            "detected_images": crops
        })

    out_json = Path(json_out_dir) / f"{pdf_name}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Complete → {out_json}")
    return out_json


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_images_text.py path/to/pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print("File not found:", pdf_path)
        sys.exit(1)

    process_pdf(pdf_path)

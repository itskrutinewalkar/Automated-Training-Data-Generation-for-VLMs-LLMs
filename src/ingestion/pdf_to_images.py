"""
pdf_to_images.py
----------------
Converts all pages of a PDF file into images using pdf2image.

Input:  data/raw/<your_pdf_file>.pdf
Output: data/processed/images/<pdf_name>_page_<n>.jpg
"""

import os
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

def pdf_to_images(pdf_path, output_dir="data/processed/images"):
    """
    Converts PDF pages into individual JPEG images.
    Args:
        pdf_path (str): Path to input PDF file.
        output_dir (str): Directory to save output images.
    Returns:
        list: Paths of generated image files.
    """
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    # Convert PDF pages to images
    pages = convert_from_path(pdf_path, dpi=300)  # 300 DPI = good quality
    image_paths = []

    # Save each page as an image
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    for i, page in enumerate(pages):
        image_path = os.path.join(output_dir, f"{pdf_name}_page_{i+1}.jpg")
        page.save(image_path, "JPEG")
        image_paths.append(image_path)

    print(f"[INFO] Converted {len(pages)} pages from {pdf_path} to {output_dir}")
    return image_paths


if __name__ == "__main__":
    # Example usage
    input_pdf = "data/raw/manual.pdf"  # put your test PDF here
    output_folder = "data/processed/images"

    if not os.path.exists(input_pdf):
        print(f"[ERROR] File not found: {input_pdf}")
    else:
        pdf_to_images(input_pdf, output_folder)

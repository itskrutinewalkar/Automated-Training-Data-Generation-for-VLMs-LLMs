import os
from src.ingestion.pdf_to_images import pdf_to_images
from src.ingestion.ocr_extraction import extract_text_from_images
from src.cleaning.cleaning_pipeline import save_cleaned_pages
from src.cleaning.text_cleaner import clean_text, count_words

RAW_DIR = "data/raw"
CLEANED_DIR = "data/cleaned"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEANED_DIR, exist_ok=True)

def process_pdf(uploaded_files):
    """
    Accepts multiple Streamlit UploadedFile objects,
    produces ONE cleaned JSON file
    """

    all_pages = []
    page_counter = 1

    for uploaded_file in uploaded_files:
        # Save PDF to disk
        pdf_path = os.path.join(RAW_DIR, uploaded_file.name)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        # PDF -> Images
        images = pdf_to_images(pdf_path)

        # OCR
        ocr_pages = extract_text_from_images(images)

        # Merge pages and create cleaned text
        for page in ocr_pages:
            raw = page.get("raw_text") or page.get("text", "")
            cleaned = clean_text(raw)

            all_pages.append({
                "page_number": page_counter,
                "raw_text": raw,
                "clean_text": cleaned,
                "word_count": count_words(raw),
                "source_pdf": uploaded_file.name
            })
            page_counter += 1
    # Save cleaned JSO
    output_path = os.path.join(CLEANED_DIR, "combined_cleaned.json")
    save_cleaned_pages(all_pages, output_path)

    return {
        "cleaned": output_path
    }

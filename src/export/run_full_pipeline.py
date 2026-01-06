from src.ingestion.ingestion_pipeline import process_pdf
from src.annotation.pipeline import run_annotation_and_qa
from src.cleaning.cleaning_pipeline import get_latest_cleaned_file

def run(uploaded_files=None, cleaned_json_path=None, progress_callback=None):
    def update(message, percent):
        if progress_callback:
            progress_callback(message, percent)

    update("Starting Annotation and QA Pipeline...", 0)

    # Ingestion Step (if uploaded_file is provided)
    if uploaded_files:
        update("Running OCR and PDF ingestion", 20)
        ingestion_outputs = process_pdf(uploaded_files=uploaded_files)
        cleaned_path = ingestion_outputs["cleaned"]

    elif cleaned_json_path:
        ingestion_outputs = {}
        cleaned_path = cleaned_json_path
        update("Using provided cleaned JSON", 20)

    else:
        ingestion_outputs = {}
        cleaned_path = get_latest_cleaned_file()
        update("Using latest cleaned JSON", 20)

    update("PDF ingestion and text cleaning completed", 50)

    # Annotation and QA Step
    update("Running annotation and QA generation", 70)

    qa_outputs = run_annotation_and_qa(
        cleaned_json_path=cleaned_path
    )

    update("Annotation and QA generation completed", 95)

    # Completion stage
    update("Finalizing outputs", 100)

    return {
        **ingestion_outputs,
        **qa_outputs
    }
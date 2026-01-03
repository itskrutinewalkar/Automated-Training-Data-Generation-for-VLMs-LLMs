import os
from src.annotation.qa_pipeline import QAPipeline

def run_annotation_and_qa(cleaned_json_path):
    """
    Takes cleaned OCR JSON and produces:
    1. Annotated JSON
    2. QA dataset JSON
    """

    base_name = os.path.basename(cleaned_json_path).replace("_cleaned.json", "")

    # -----------------------------
    # Ensure folders
    # -----------------------------
    os.makedirs("data/final", exist_ok=True)

    # -----------------------------
    # Step 4: QA Generation
    # -----------------------------
    qa_output_path = f"data/final/{base_name}_qa.json"

    qa_pipeline = QAPipeline()
    qa_pipeline.process(
        input_path=cleaned_json_path,
        output_path=qa_output_path
    )

    return {
        "qa": qa_output_path
    }
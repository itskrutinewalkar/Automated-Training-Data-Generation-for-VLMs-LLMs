import streamlit as st
import time
import os
import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the pipeline
try:
    from src.export.run_full_pipeline import run
except ImportError:
    # Fallback for UI testing if backend isn't linked
    def run(uploaded_file):
        time.sleep(2) # Simulate work
        return {
            "Images_ZIP": "data/final/images.zip",
            "Annotations_JSON": "data/final/annotations.jsonl",
            "QA_Dataset_CSV": "data/final/qa_dataset.csv"
        }

if "start_time" not in st.session_state:
    st.session_state.start_time = None  
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "outputs" not in st.session_state:
    st.session_state.outputs = None

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Automated Dataset Generation",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
body {
    font-family: 'Inter', sans-serif;
}

.center {
    text-align: center;
}

p {
    line-height: 1.6;
    text-align: left;
}
            
.card {
    background-color: #EAF7EA;
    padding: 1.4rem;
    border-radius: 14px;
    margin-bottom: 1.2rem;
}


.success-tick {
    font-size: 22px;
    font-weight: 600;
    color: #2ecc71;
}

.st-key-analysis_container {
    background-color: #CFFFC9;
    border-radius: 14px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)



# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Run Pipeline", "Results"])

st.sidebar.markdown("""
### Project Scope
• OCR & PDF Ingestion  
• Text Cleaning  
• QA Annotation  
• LLM / VLM Dataset Export  
""")

# -------------------- HOME --------------------
if page == "Home":
    st.markdown("<h1 class='center'>Automated Training Data Generation</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("""
        <div class="card">
        <h3>Overview</h3>
        <p>
        This system automatically converts unstructured PDF documents into
        structured datasets suitable for fine-tuning Large Language Models (LLMs)
        and Vision-Language Models (VLMs).
        </p>
        <p>
        The pipeline performs OCR, text cleaning, annotation, and question-answer
        generation with minimal human intervention.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.image("assets/system_architecture.png", use_container_width=True)

# -------------------- RUN PIPELINE --------------------
elif page == "Run Pipeline":
    st.header("Run Dataset Generation Pipeline")

    st.markdown("""
    <div class="card">
    <b>Pipeline Stages</b><br>
    1. PDF Ingestion & OCR<br>
    2. Text Cleaning<br>
    3. Annotation & QA Generation<br>
    4. Dataset Export
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
    run_btn = st.button("Run Pipeline", type="primary", use_container_width=True)

    if uploaded_file and run_btn:
        # Initialize timing
        st.session_state.start_time = time.time()
        st.session_state.end_time = None

        with st.status("Executing Pipeline", expanded=True):

            progress_bar = st.progress(0)
            status_text = st.empty()

            def ui_progress(message, percent):
                status_text.write(message)
                progress_bar.progress(percent)

            # Run pipeline
            st.session_state.outputs = run(
                uploaded_file=uploaded_file,
                progress_callback=ui_progress
            )

            # Finish timing
            st.session_state.end_time = time.time()

            # Remove progress UI
            progress_bar.empty()
            status_text.empty()

            # Success indicator
            st.markdown(
                "<div class='success-tick'>✅ Pipeline completed successfully</div>",
                unsafe_allow_html=True
            )

        time.sleep(1)  # Brief pause before navigating to results
        page = "Results"
        st.rerun()

# -------------------- RESULTS --------------------
elif page == "Results":
    st.header("Pipeline Results")

    if st.session_state.outputs is None:
        st.warning("No pipeline run yet.")
    else:
        with st.container(key="analysis_container"):

            st.subheader("Execution Summary")

            exec_time = None
            if st.session_state.start_time and st.session_state.end_time:
                exec_time = round(
                    st.session_state.end_time - st.session_state.start_time, 2
                )

            c1, c2, c3 = st.columns(3)
            c1.metric("Status", "Completed")
            c2.metric("Files Generated", len(st.session_state.outputs))
            c3.metric("Execution Time (s)", exec_time if exec_time else "—")

            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("Downloads")
        st.caption("Generated datasets and intermediate outputs")

        for key, value in st.session_state.outputs.items():
            if isinstance(value, str):
                with open(value, "rb") as f:
                    st.download_button(
                        label=f"Download {key.replace('_', ' ').title()}",
                        data=f,
                        file_name=value.split("/")[-1],
                        mime="application/json"
                    )

import json
from tqdm import tqdm

from src.annotation.text_chunker import chunk_text
from src.annotation.question_generator import QuestionGenerator
from src.annotation.answer_extractor import AnswerExtractor
from src.config import MIN_ANSWER_SCORE, MIN_ANSWER_LENGTH

class QAPipeline:
    def __init__(self):
        self.qg = QuestionGenerator()
        self.qa = AnswerExtractor()

    def process(self, input_path, output_path):
        with open(input_path, "r") as f:
            pages = json.load(f)

        qa_pairs = []

        for page in tqdm(pages, desc="Annotating pages"):
            page_number = page["page_number"]
            text = page["clean_text"]

            for chunk in chunk_text(text):
                try:
                    questions = self.qg.generate(chunk)

                    for question in questions:
                        answer, score = self.qa.extract(question, chunk)

                        if score >= MIN_ANSWER_SCORE and len(answer.strip()) >= MIN_ANSWER_LENGTH:
                            qa_pairs.append({
                                "page_number": page_number,
                                "question": question,
                                "answer": answer,
                                "context": chunk
                            })
                except Exception:
                    continue

        with open(output_path, "w") as f:
            json.dump(qa_pairs, f, indent=2)

        if len(qa_pairs) == 0:
            print("\n⚠️ No valid QA pairs were generated. Try adjusting the thresholds or check the input data.")
        print(f"\n✅ Generated {len(qa_pairs)} QA pairs")

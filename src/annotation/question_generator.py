from transformers import T5Tokenizer, T5ForConditionalGeneration
from src.config import QG_MODEL

class QuestionGenerator:
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained(QG_MODEL)
        self.model = T5ForConditionalGeneration.from_pretrained(QG_MODEL)

    def generate(self, context):
        input_text = "generate question: " + context
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True
        )

        outputs = self.model.generate(
            **inputs,
            max_length=64,
            num_beams=5,
            num_return_sequences=3,
            do_sample=True,
            temperature=0.9
        )

        # 🔥 Decode ALL questions
        questions = [
            self.tokenizer.decode(o, skip_special_tokens=True)
            for o in outputs
        ]

        return questions

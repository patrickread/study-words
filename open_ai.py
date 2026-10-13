import openai
import os
from typing import Optional


class OpenAI:
    def __init__(self):
        super().__init__()
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def generate_sentence(self, word: str) -> Optional[str]:
        if openai.api_key is None:
            return None

        completion_result = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Use the word \"{word}\" in a sentence."}
            ],
            temperature=0.5,
            max_tokens=150,
            top_p=1,
            frequency_penalty=1,
            presence_penalty=1,
        )
        sentence = completion_result["choices"][0]["message"]["content"]
        return sentence.replace("\n", "")

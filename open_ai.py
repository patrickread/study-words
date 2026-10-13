import os
from typing import Optional

from openai import OpenAI as OpenAIClient


class OpenAI:
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAIClient(api_key=self.api_key) if self.api_key else None

    def generate_sentence(self, word: str) -> Optional[str]:
        if self.client is None:
            return None

        response = self.client.chat.completions.create(
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
        sentence = response.choices[0].message.content or ""
        return sentence.replace("\n", "")

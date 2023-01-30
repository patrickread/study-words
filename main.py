import random
import subprocess
import re
from open_ai import OpenAI
from pathlib import Path
from typing import Optional


QUESTION_INPUT_TEXT = "?"  # Used if you're unsure of prompt. Will repeat
GAME_LENGTH = 10  # Number of sight words to practice each round
FAILURE_TOLERANCE = 2  # How many times to fail before switch words to prevent burnout


path = Path(__file__).parent


with (path / "words.txt").open("r") as text_file:
    text = text_file.read()
    words = [line for line in text.split("\n") if line]

with (path / "affirmations.txt").open("r") as text_file:
    text = text_file.read()
    affirmations = [line for line in text.split("\n") if line]


def speak(input: str):
    subprocess.call(["say", input])


def check_gibberish(input: str) -> bool:
    if len(input) > 20:
        return True

    if re.match(r"(.*)([^A-Za-z0-9'])(.*)", input):
        return True

    return False


def get_attempt(name: str, word: str, sentence: Optional[str]):
    prompt = f"{name} your word is {word}."
    if sentence:
        prompt +=  f" As in, {sentence}"

    attempt = QUESTION_INPUT_TEXT

    while attempt == QUESTION_INPUT_TEXT:
        speak(prompt)
        attempt = input("Write word > ")
        attempt = attempt.strip()

    return attempt


def practice_words(input_words: list[str]):
    words_to_practice = input_words.copy()
    random.shuffle(words_to_practice)
    correct_words = []
    failures = 0
    openai_generator = OpenAI()

    speak("Welcome to the sight word game! First, what is your name?")
    name = input("What is your name? > ")
    speak(f"Hi, {name}! Let's play!")

    while words_to_practice and len(correct_words) < GAME_LENGTH:
        word = words_to_practice[0]
        sentence = openai_generator.generate_sentence(word)
        attempt = get_attempt(name, word, sentence)

        while check_gibberish(attempt):
            speak(f"{name}, it seems like you just typed gibberish. Let's try again.")
            attempt = get_attempt(name, word, sentence)

        success = attempt.lower() == word.lower()
        affirmation = random.choice(affirmations)
        response_to_success = f"That is correct! {affirmation}" if success else "That is not correct."
        speak(f"{name}, you wrote {attempt}. {response_to_success}")

        if success:
            correct_words.append(word)
            del words_to_practice[0]
            failures = 0
        else:
            failures += 1

        if failures > FAILURE_TOLERANCE-1 and len(words_to_practice) > 1:
            speak("Let's try a different word")
            random.shuffle(words_to_practice)
            failures = 0

    speak(f"{name} you did it! You finished this round of sight words. I'm so proud of you.")

practice_words(words)

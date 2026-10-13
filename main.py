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


WORD_LISTS = {
    "1": ("Sight words", "words.txt"),
    "2": ("Addie's spelling list D-1", "words-addie-d1.txt"),
}


def load_words(filename: str) -> list[str]:
    with (path / filename).open("r") as text_file:
        text = text_file.read()
        return [line.strip() for line in text.split("\n") if line.strip()]


def choose_word_list(name: str) -> list[str]:
    print("Choose a word list:")
    for key, (label, _) in WORD_LISTS.items():
        print(f"  {key}) {label}")
    speak(f"{name}, which list do you want to practice? Press 1 for sight words, or 2 for Addie's spelling list.")
    choice = input("Choose a list > ").strip()
    while choice not in WORD_LISTS:
        speak("Hmm, I didn't catch that. Please press 1 or 2.")
        choice = input("Choose a list > ").strip()
    return load_words(WORD_LISTS[choice][1])

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

    while attempt == "":
        attempt = input().strip()

    return attempt


def practice_words():
    correct_words = []
    failures = 0
    openai_generator = OpenAI()

    speak("Welcome to the sight word game! First, what is your name?")
    name = input("What is your name? > ")
    speak(f"Hi, {name}! Let's play!")

    words_to_practice = choose_word_list(name)
    random.shuffle(words_to_practice)

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

practice_words()

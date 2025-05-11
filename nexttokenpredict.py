import requests
import random
import re

def get_book_text():
    #load Ramayana book text from Project Gutenberg
    url='https://www.gutenberg.org/cache/epub/73417/pg73417.txt'
    response = requests.get(url)
    text = response.text
    return text

def get_good_sentences(text, min_length=15, max_length=30):
    #Get Sentences with appropriate length
    sentences = re.findall(r'[A-Z][^.!?]*[.!?]', text)
    good_sentences = []
    for s in sentences:
        s = s.strip()
        words = s.split()
        if min_length <= len(words) <= max_length:
            good_sentences.append(s)
    return good_sentences

def play_continuous_game(sentences, num_sentences=3):
    """Play continuous prediction within each sentence"""
    print("Welcome to Continuous Next Token Prediction!")
    print("After each prediction, I'll show the correct word")
    print("and ask you to predict the next one.\n")

    score = 0
    total_predictions = 0

    for round_num in range(1, num_sentences+1):
        # Select a sentence
        sentence = sentences[round_num % len(sentences)]
        words = sentence.split()

        # Start with first 5 words
        revealed_count = 5
        revealed = words[:revealed_count]

        print(f"\n--- Sentence {round_num}/{num_sentences} ---")
        print(f"Starting context: \"{' '.join(revealed)}...\"")

        # Continue predicting until end of sentence
        while revealed_count < len(words):
            # Get prediction for next word
            print("\nPredict the next word:")
            prediction = input("> ").strip().lower()

            # Clean prediction (first word only)
            if " " in prediction:
                prediction = prediction.split()[0]
            prediction = re.sub(r'[^\w\']', '', prediction)

            # Get actual next word
            next_word = words[revealed_count]
            clean_next = re.sub(r'[^\w\']', '', next_word.lower())

            # Score
            if prediction == clean_next:
                result = "CORRECT!"
                round_score = 1
            else:
                result = "INCORRECT"
                round_score = 0

            score += round_score
            total_predictions += 1

            # Show result
            print(f"{result} The next word is: \"{next_word}\"")

            # Reveal next word
            revealed_count += 1
            revealed = words[:revealed_count]
            print(f"Context now: \"{' '.join(revealed)}...\"")

            # If near end, show how many words remain
            if len(words) - revealed_count <= 3:
                print(f"({len(words) - revealed_count} words remaining in this sentence)")

        # Show complete sentence
        print(f"\nComplete sentence: \"{sentence}\"")
        print(f"You made {total_predictions} predictions in this round.")

    # Final score
    accuracy = (score / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"\nGame Over! You got {score} out of {total_predictions} correct.")
    print(f"Accuracy: {accuracy:.1f}%")

    if accuracy > 20:
        print("Excellent! You're showing strong language prediction skills.")
    elif accuracy > 10:
        print("Good job! You're better than random guessing.")
    else:
        print("Keep practicing! Next-token prediction is challenging.")

# Load the text and get good sentences
print("Loading text...")
text = get_book_text()
sentences = get_good_sentences(text)
print(f"Found {len(sentences)} good sentences!")

# Start the game with 5 rounds
play_continuous_game(sentences, 3)

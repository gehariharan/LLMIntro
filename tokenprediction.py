# Import the AutoModelForCausalLM class from the transformers library
from transformers import AutoModelForCausalLM, AutoTokenizer

# Define the model name/identifier for a small language model from HuggingFace
model_name="HuggingFaceTB/SmolLM2-135M-Instruct"

# Load the pre-trained causal language model
# .to("cpu") explicitly places the model on CPU rather than GPU
model = AutoModelForCausalLM.from_pretrained(model_name).to("cpu")
tokenizer=AutoTokenizer.from_pretrained(model_name)

import torch
import torch.nn.functional as F
def predict_next_token(text, num_tokens=5, temperature=0):
    # Convert text to model format
    tokens = tokenizer.encode(text, return_tensors="pt")

    # Get model prediction
    output = model(tokens)

    # Focus on the last position (next token)
    next_token_scores = output.logits[0, -1, :]

    #Apply temperature (higher = more random)
    if temperature > 0:
        next_token_scores = next_token_scores / temperature

    # Convert scores to probabilities (0-1)
    probabilities = F.softmax(next_token_scores, dim=-1)

    # Get top predictions
    top_probs, top_ids = torch.topk(probabilities, num_tokens)

    # Show results
    print(f"After '{text}', the model predicts:")
    print("-" * 80)
    print("Top tokens possible: ",top_ids)
    for i, (prob, token_id) in enumerate(zip(top_probs, top_ids)):
        token_text = tokenizer.decode(token_id)
        percentage = prob * 100
        print(f"{i+1}. '{token_text}',  - {percentage:.1f}%, id: {token_id}")

    # Sample the next token based on the probability distribution
    next_token_id = torch.multinomial(probabilities, num_samples=1).item()
    next_token_text = tokenizer.decode(next_token_id)
    next_token_prob = probabilities[next_token_id].item() * 100

    print(f"FINAL PREDICTION: '{next_token_text}' ({next_token_prob:.1f}%)")
    return next_token_text

def generate_text(text, max_length=100, top_k=5,temperature=1):
    # Keep track of original input
    original_text = text
    generated_tokens = 0

    # Generate tokens one by one (autoregressive)
    for i in range(1, max_length + 1):
        # Predict next token using our earlier function
        new_token = predict_next_token(text, top_k, temperature)

        text = text + new_token
        generated_tokens += 1

        # Show progress
        print(f"Token {i}: '{new_token}'")
        print(f"Text so far: '{text}'")
        print("-" * 40)

        # Stop if we get an end marker
        if new_token == "<|endoftext|>":
            break

    print(f"\nFINAL RESULT:")
    print(f"Original prompt: '{original_text}'")
    print(f"Generated {generated_tokens} new tokens")
    print(f"Complete text: '{text}'")

    return text

predict_next_token("The capital of Russia was", num_tokens=10, temperature=1)
generate_text("The capital of Russia was ", max_length=10, top_k=5, temperature=1)

# Import the AutoTokenizer class from the transformers library
from transformers import AutoTokenizer

# Define model identifiers for different LLMs
model1 = "deepseek-ai/DeepSeek-R1"  # DeepSeek model
model2 = "microsoft/phi-4"          # Microsoft's Phi-4 model
model3 = "NousResearch/Llama-2-7b-chat-hf"  # Llama 2 model

# Load the tokenizer for the Phi-4 model
tokenizer = AutoTokenizer.from_pretrained(model2)

# Print the vocabulary size (number of tokens the model knows)
print(len(tokenizer))

# Get the complete vocabulary dictionary (maps tokens to their IDs)
vocab = tokenizer.get_vocab()

# Display the first 10 tokens from the vocabulary for inspection
sample_tokens = list(vocab.items())[:10]  # First 10 tokens  
for token, token_id in sample_tokens:
    print(f"Token: {repr(token)}, ID: {token_id}")

# Example text to demonstrate tokenization
text = "Hello, this is an example of tokenization!"

# Break the text into tokens using the tokenizer
tokens = tokenizer.tokenize(text)

# Convert the text to token IDs (numbers the model actually uses)
token_ids = tokenizer.encode(text)

# Print the results of tokenization
print(f"\nTokenized text: {tokens}")
print(f"Token IDs: {token_ids}")

# Example of tokenizing a sentence
word = "How are you liking Vibe coding?"
toks = tokenizer.encode(word, add_special_tokens=False)  # Avoid special tokens for cleaner output
tokens = tokenizer.tokenize(word)

# Print a table of tokens, IDs, and decoded text
print("\nTokenization of the sentence:{word}")
print("-" * 60)
print(f"{'Index':<8}{'Token':<20}{'ID':<10}{'Decoded':<20}")
print("-" * 60)

for i, (token, id) in enumerate(zip(tokens, toks)):
    decoded = tokenizer.decode([id])
    print(f"{i:<8}{token:<20}{id:<10}{decoded:<20}")

print("-" * 60)
print(f"Full word: {word}")
print(f"Full decoded: {tokenizer.decode(toks)}")


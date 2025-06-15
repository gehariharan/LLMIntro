import gradio as gr
import os

# Configuration
DEBUG_MODE = False  # Set to False to disable debug information
ASSETS_FOLDER = "assets"

# Check if the assets folder and image exist, otherwise use a fallback URL
BLUEY_GIF_FILENAME = "bluey.gif"
BLUEY_IMAGE_PATH = os.path.join(ASSETS_FOLDER, BLUEY_GIF_FILENAME)
BLUEY_FALLBACK_URL = "https://i.imgur.com/JYoUEG0.png"  # Fallback online image

# Use local file if it exists, otherwise use fallback URL
if os.path.exists(BLUEY_IMAGE_PATH):
    BLUEY_IMAGE_URL = BLUEY_IMAGE_PATH
    print(f"Using local Bluey image: {os.path.abspath(BLUEY_IMAGE_PATH)}")
else:
    BLUEY_IMAGE_URL = BLUEY_FALLBACK_URL
    print(f"Local Bluey image not found at {os.path.abspath(BLUEY_IMAGE_PATH)}. Using fallback URL.")

# Constants for repeated strings
CHATBOT_TITLE = "Bluey Chatbot"
CHATBOT_DESCRIPTION = "This chatbot talks like Bluey from the popular children's show, using a playful, imaginative style with emojis!"

# Simple interface without debug information
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(BLUEY_IMAGE_URL, show_label=False, height=150)
        with gr.Column(scale=3):
            gr.Markdown(f"<h1 style='font-size: 2.5em; font-weight: bold; margin-bottom: 0.5em; color: #1E88E5;'>{CHATBOT_TITLE} 🐾</h1>")
            gr.Markdown(f"<p style='font-size: 1.2em; color: #42A5F5;'>{CHATBOT_DESCRIPTION}</p>")

    chatbot = gr.Chatbot(
        type="messages",
        avatar_images=(os.path.join(ASSETS_FOLDER, "human.png"), os.path.join(ASSETS_FOLDER, "blueybot.png")),
    )
    msg = gr.Textbox(placeholder="Type your message to Bluey here...", show_label=False)

    def simple_chat(message, history):
        # Simple echo response for testing
        return f"You said: {message}"

    msg.submit(simple_chat, [msg, chatbot], [msg, chatbot])

    with gr.Accordion("Example Questions", open=False):
        gr.Examples(
            examples=[
                "What games do you like to play?",
                "Can you tell me about Australia?",
                "How do I make friends at school?",
                "What's your favorite animal?",
                "Tell me about the solar system"
            ],
            inputs=msg
        )

# Launch the demo
print("Launching Gradio interface...")
demo.launch()
print("Gradio interface closed.")

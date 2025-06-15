import gradio as gr
import os

# Constants
ASSETS_FOLDER = "assets"
HUMAN_IMAGE_PATH = os.path.join(ASSETS_FOLDER, "human.png")
BLUEYBOT_IMAGE_PATH = os.path.join(ASSETS_FOLDER, "blueybot.png")

# Check if the assets folder and images exist
if os.path.exists(HUMAN_IMAGE_PATH):
    print(f"Human image found at: {os.path.abspath(HUMAN_IMAGE_PATH)}")
else:
    print(f"Human image NOT found at: {os.path.abspath(HUMAN_IMAGE_PATH)}")

if os.path.exists(BLUEYBOT_IMAGE_PATH):
    print(f"Blueybot image found at: {os.path.abspath(BLUEYBOT_IMAGE_PATH)}")
else:
    print(f"Blueybot image NOT found at: {os.path.abspath(BLUEYBOT_IMAGE_PATH)}")

# Create a simple Gradio interface to test the avatar images
with gr.Blocks() as demo:
    gr.Markdown("# Avatar Image Test")
    
    chatbot = gr.Chatbot(
        type="messages",
        avatar_images=(HUMAN_IMAGE_PATH, BLUEYBOT_IMAGE_PATH),
    )
    
    msg = gr.Textbox(placeholder="Type a message to test the avatars")
    
    def respond(message, history):
        history.append((message, "This is a test response"))
        return "", history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    
    gr.Markdown("## Image Preview")
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Human Avatar")
            gr.Image(HUMAN_IMAGE_PATH, height=150)
        with gr.Column():
            gr.Markdown("### Blueybot Avatar")
            gr.Image(BLUEYBOT_IMAGE_PATH, height=150)

# Launch the demo
if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch()
    print("Gradio interface closed.")

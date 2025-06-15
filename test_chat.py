import gradio as gr
import os

# Constants
ASSETS_FOLDER = "assets"

# Create a simple Gradio interface to test the chat functionality
with gr.Blocks() as demo:
    gr.Markdown("# Chat Test")
    
    chatbot = gr.Chatbot(
        type="messages",
        avatar_images=(os.path.join(ASSETS_FOLDER, "human.png"), os.path.join(ASSETS_FOLDER, "blueybot.png")),
    )
    
    msg = gr.Textbox(placeholder="Type a message to test the chat")
    
    def respond(message, history):
        # Simple echo response for testing
        return "", history + [(message, f"You said: {message}")]
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])

# Launch the demo
if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch()
    print("Gradio interface closed.")

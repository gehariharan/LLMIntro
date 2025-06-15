import gradio as gr
import numpy as np
from fastrtc import WebRTC, ReplyOnPause

def response(audio: tuple[int, np.ndarray]):
    """This function must yield audio frames"""
    ...
    yield audio


with gr.Blocks() as demo:
    gr.HTML(
    """
    <h1 style='text-align: center'>
    Chat (Powered by WebRTC ⚡️)
    </h1>
    """
    )
    with gr.Column():
        with gr.Group():
            audio = WebRTC(
                mode="send-receive",
                modality="audio",
            )
        audio.stream(fn=ReplyOnPause(response),
                    inputs=[audio], outputs=[audio],
                    time_limit=60)
demo.launch()
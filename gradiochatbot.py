from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import GROQ_API_KEY, GROQ_MODEL_NAME
llm_groq = ChatGroq(model_name=GROQ_MODEL_NAME, api_key=GROQ_API_KEY)

import gradio as gr

def chat(message, history):
    return llm_groq.invoke(message).content


demo = gr.ChatInterface(
    fn=chat,
    title="Simple Chatbot",
    description="This is a chatbot built using gradio",
)



demo.launch(debug=True)

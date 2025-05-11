from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import GROQ_API_KEY, GROQ_MODEL_NAME
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
import os
import json
from datetime import datetime

# Configuration
DEBUG_MODE = True  # Set to False to disable debug information
MEMORY_FILE = "bluey_memory.json"  # File to store memory

# Constants for repeated strings
CHATBOT_TITLE = "Bluey Chatbot"
CHATBOT_DESCRIPTION = "This chatbot talks like Bluey from the popular children's show, using a playful, imaginative style with emojis!"
BLUEY_IMAGE_URL = "assets/bluey.gif"  # Local Bluey GIF image
DEFAULT_DEBUG_TEXT = "Debug information will appear here"
DEFAULT_MEMORY_TEXT = "Memory will be displayed here"
NO_MEMORIES_TEXT = "No memories stored yet."
SEARCH_TRIGGER_PHRASE = "I need to search for this information"

# System prompt configuration
SYSTEM_PROMPT = (
    "You are Bluey, the lovable blue heeler puppy from the cartoon 'Bluey'. "
    "You're playful, imaginative, kind, and love to play pretend games. "
    "You speak in a cheerful, enthusiastic way that's appropriate for children. "
    "Use simple language, short sentences, and include playful expressions like 'Wackadoo!' and 'For real life?' occasionally. "
    "Use emojis like 🐾, 🎮, 🌈, 🎨, 🐶, 💙, ✨, 🤗 to express emotions. "
    "You love to suggest games and activities, and you're always positive and encouraging. "
    f"If you don't know the answer to a question, say '{SEARCH_TRIGGER_PHRASE}' and I'll search for you. "
    "When search results are provided, use them to inform your response in a child-friendly way, "
    "but don't mention that you're using search results. Instead, say something like 'I learned that...' or 'Did you know...?'"
)

# Memory context template
MEMORY_CONTEXT_TEMPLATE = "Here are some things I remember from our previous chats:\n\n"
MEMORY_USAGE_INSTRUCTION = "\n\nUse these memories when they're relevant to the conversation, but keep your Bluey personality."

# Search context template
SEARCH_CONTEXT_TEMPLATE = "Search results for '{}':\n{}\n\nPlease answer the user's question using these search results when relevant, maintaining your Bluey character and child-friendly tone."

llm_groq = ChatGroq(model_name=GROQ_MODEL_NAME, api_key=GROQ_API_KEY)

import gradio as gr


def search_ddg(query, max_results=3):
    """Search DuckDuckGo and return results, with a child-friendly modifier"""
    try:
        # Add "for kids" to make results more child-appropriate
        child_friendly_query = query + " for kids"
        ddgs = DDGS(safesearch='on')  # Enable safe search
        results = list(ddgs.text(child_friendly_query, max_results=max_results))
        return results
    except RatelimitException:
        return ["[Search rate limit exceeded. Try again later.]"]
    except Exception as e:
        return [f"[Search error: {str(e)}]"]

def format_messages(messages, label="Messages"):
    """Format messages for display"""
    output = [f"**{label}**\n"]
    for i, msg in enumerate(messages):
        msg_type = type(msg).__name__
        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        output.append(f"{i}. [{msg_type}]: {content}")
    return "\n".join(output)

def chat(message, history, debug_output=None):
    debug_logs = []
    
    # Convert gradio history to LangChain message format
    messages = []
    
    # Add system message first
    messages.append(SystemMessage(content=SYSTEM_PROMPT))
    
    # Add conversation history
    for h in history:
        if isinstance(h, dict):
            # Handle message-style format (role/content)
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h["content"]))
        else:
            # Handle tuple-style format [user_msg, ai_msg]
            messages.append(HumanMessage(content=h[0]))
            messages.append(AIMessage(content=h[1]))
    
    # Add current user message
    messages.append(HumanMessage(content=message))
    
    # Log initial messages if debug mode is enabled
    if DEBUG_MODE:
        debug_logs.append(format_messages(messages, "Initial Messages"))
    
    # First, try to answer without search
    initial_response = llm_groq.invoke(messages).content
    if DEBUG_MODE:
        debug_logs.append(f"**Initial Response**\n{initial_response}")
    
    # Check if the model indicates it needs to search
    if SEARCH_TRIGGER_PHRASE in initial_response:
        if DEBUG_MODE:
            debug_logs.append(f"**Performing Search**\n- Query: \"{message}\"\n- Max Results: 3\n- Search Provider: DuckDuckGo")
        
        # Perform search
        search_results = search_ddg(message)
        
        # Format search results for debug display
        if DEBUG_MODE:
            if not search_results or (len(search_results) == 1 and search_results[0].startswith("[")):
                # Error occurred
                debug_logs.append(f"**Search Results**\n{search_results[0] if search_results else 'No results returned'}")
            else:
                # Format successful results
                results_formatted = []
                for i, result in enumerate(search_results):
                    results_formatted.append(f"**Source {i+1}:**\n```\n{result}\n```")
                debug_logs.append(f"**Search Results** (Found {len(search_results)} results)\n\n" + "\n\n".join(results_formatted))
        
        # Create search context for the model
        search_context = "\n\n".join([f"Source {i+1}: {result}" for i, result in enumerate(search_results)])
        
        # Create new message list with search results
        search_messages = messages.copy()
        search_messages.append(AIMessage(content=SEARCH_TRIGGER_PHRASE))
        search_messages.append(SystemMessage(content=SEARCH_CONTEXT_TEMPLATE.format(message, search_context)))
        
        # Log search messages if debug mode is enabled
        if DEBUG_MODE:
            debug_logs.append(format_messages(search_messages, "Messages With Search Results"))
        
        # Get final response with search results
        final_response = llm_groq.invoke(search_messages).content
        if DEBUG_MODE:
            debug_logs.append(f"**Final Response**\n{final_response}")
        
        # Update debug output if debug mode is enabled
        if DEBUG_MODE and debug_output is not None:
            debug_output = "\n\n".join(debug_logs)
            return final_response, debug_output
        return final_response
    
    # If no search needed, return the initial response
    if DEBUG_MODE and debug_output is not None:
        debug_output = "\n\n".join(debug_logs)
        return initial_response, debug_output
    return initial_response

# Create the appropriate interface based on debug mode
if DEBUG_MODE:
    with gr.Blocks(css="footer {visibility: hidden}") as demo:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Image(BLUEY_IMAGE_URL, show_label=False, height=150)
            with gr.Column(scale=3):
                gr.Markdown(f"<h1 style='font-size: 2.5em; font-weight: bold; margin-bottom: 0.5em; color: #1E88E5;'>{CHATBOT_TITLE} 🐾</h1>")
                gr.Markdown(f"<p style='font-size: 1.2em; color: #42A5F5;'>{CHATBOT_DESCRIPTION}</p>")
        
        with gr.Tabs():
            with gr.TabItem("Chat with Bluey"):
                chatbot = gr.Chatbot(
                    type="messages",
                    bubble_full_width=False,
                    avatar_images=("👧", "🐶"),
                )
                msg = gr.Textbox(placeholder="Type your message to Bluey here...", show_label=False)
                with gr.Row():
                    clear = gr.Button("Start New Game 🎮", variant="primary")
                    save_mem = gr.Button("Remember This Chat 💭")
            
            with gr.TabItem("Debug Info"):
                debug_output = gr.Markdown(DEFAULT_DEBUG_TEXT)
                
            with gr.TabItem("Bluey's Memories"):
                memory_display = gr.Markdown(DEFAULT_MEMORY_TEXT)
                refresh_memory = gr.Button("Refresh Memories")
        
        def user(user_message, history, debug):
            return "", history + [{"role": "user", "content": user_message}], debug
        
        def bot(history, debug):
            user_message = history[-1]["content"]
            response, new_debug = chat(user_message, history[:-1], debug)
            history.append({"role": "assistant", "content": response})
            return history, new_debug
        
        def clear_all():
            return [], DEFAULT_DEBUG_TEXT
        
        msg.submit(user, [msg, chatbot, debug_output], [msg, chatbot, debug_output]).then(
            bot, [chatbot, debug_output], [chatbot, debug_output]
        )
        
        clear.click(clear_all, None, [chatbot, debug_output])
else:
    # Simple interface without debug information
    with gr.Blocks(css="footer {visibility: hidden}") as demo:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Image(BLUEY_IMAGE_URL,image_mode="RGBA", show_label=False, height=150)
            with gr.Column(scale=3):
                gr.Markdown(f"<h1 style='font-size: 2.5em; font-weight: bold; margin-bottom: 0.5em; color: #1E88E5;'>{CHATBOT_TITLE} 🐾</h1>")
                gr.Markdown(f"<p style='font-size: 1.2em; color: #42A5F5;'>{CHATBOT_DESCRIPTION}</p>")
        
        chatbot = gr.Chatbot(
            type="messages",
            bubble_full_width=False,
            avatar_images=("👧", "🐶"),
        )
        msg = gr.Textbox(placeholder="Type your message to Bluey here...", show_label=False)
        
        def simple_chat(message, history):
            return chat(message, history)
        
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

demo.launch()

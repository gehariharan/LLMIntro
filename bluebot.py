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

# Check if the assets folder and image exist, otherwise use a fallback URL
ASSETS_FOLDER = "assets"
BLUEY_GIF_FILENAME = "bluey.gif"
BLUEY_IMAGE_PATH = os.path.join(ASSETS_FOLDER, BLUEY_GIF_FILENAME)
BLUEY_FALLBACK_URL = "https://i.imgur.com/JYoUEG0.png"  # Fallback online image

# Create assets folder if it doesn't exist
if not os.path.exists(ASSETS_FOLDER):
    os.makedirs(ASSETS_FOLDER)
    print(f"Created assets folder at {os.path.abspath(ASSETS_FOLDER)}")

# Use local file if it exists, otherwise use fallback URL
if os.path.exists(BLUEY_IMAGE_PATH):
    BLUEY_IMAGE_URL = BLUEY_IMAGE_PATH
    print(f"Using local Bluey image: {os.path.abspath(BLUEY_IMAGE_PATH)}")
else:
    BLUEY_IMAGE_URL = BLUEY_FALLBACK_URL
    print(f"Local Bluey image not found at {os.path.abspath(BLUEY_IMAGE_PATH)}. Using fallback URL.")
    print(f"To use a local image, place 'bluey.gif' in the '{ASSETS_FOLDER}' folder.")

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

# Constants for summarization
SUMMARIZE_SYSTEM_PROMPT = "You are a helpful assistant. Summarize the following conversation into a concise paragraph capturing the key information and facts discussed. Focus only on factual information that would be useful to remember for future conversations. Make it child-friendly and simple."
SUMMARIZE_HUMAN_PROMPT_TEMPLATE = "Here's the conversation to summarize:\n\n{}"
SUMMARIZE_ERROR_TEMPLATE = "Conversation on {} (failed to summarize)"

llm_groq = ChatGroq(model_name=GROQ_MODEL_NAME, api_key=GROQ_API_KEY)

import gradio as gr

def search_ddg(query):
    """Search DuckDuckGo for information"""
    try:
        # Add "for kids" to make search results more child-friendly
        safe_query = query + " for kids"
        ddgs = DDGS()
        results = list(ddgs.text(safe_query, max_results=3, safesearch='on'))

        if not results:
            return ["No search results found."]

        # Extract just the text from the results
        text_results = []
        for r in results:
            if 'body' in r:
                text_results.append(r['body'])
            elif 'snippet' in r:
                text_results.append(r['snippet'])
            else:
                # If neither body nor snippet is available, use the title
                text_results.append(r.get('title', 'No content available'))

        return text_results
    except RatelimitException:
        return ["[Search error: Rate limit exceeded. Please try again later.]"]
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

def load_memory():
    """Load memory from file"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
    return {"memories": []}

def save_memory(memory_data):
    """Save memory to file"""
    try:
        # Ensure the directory exists
        memory_dir = os.path.dirname(MEMORY_FILE)
        if memory_dir and not os.path.exists(memory_dir):
            os.makedirs(memory_dir)

        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory_data, f, indent=2)
        print(f"Memory saved to {os.path.abspath(MEMORY_FILE)}")
    except Exception as e:
        print(f"Error saving memory: {e}")

def summarize_conversation(history):
    """Summarize the conversation history using the LLM"""
    if not history:
        return None

    # Convert history to text format
    conversation_text = ""
    for msg in history:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role.capitalize()}: {content}\n"
        else:
            conversation_text += f"User: {msg[0]}\nAssistant: {msg[1]}\n"

    # Create a prompt for summarization
    summarize_prompt = [
        SystemMessage(content=SUMMARIZE_SYSTEM_PROMPT),
        HumanMessage(content=SUMMARIZE_HUMAN_PROMPT_TEMPLATE.format(conversation_text))
    ]

    try:
        # Get summary from LLM
        summary_response = llm_groq.invoke(summarize_prompt)
        return summary_response.content
    except Exception as e:
        print(f"Error summarizing conversation: {e}")
        # Return a basic timestamp-based summary as fallback
        return SUMMARIZE_ERROR_TEMPLATE.format(datetime.now().strftime("%Y-%m-%d %H:%M"))

def add_to_memory(summary):
    """Add a new memory while deduplicating similar content"""
    if not summary:
        return

    memory_data = load_memory()

    # Check for duplicates or similar content
    for existing_memory in memory_data["memories"]:
        # Simple duplicate check - could be enhanced with similarity scoring
        if summary.lower() == existing_memory["content"].lower():
            # Update timestamp instead of adding duplicate
            existing_memory["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_memory(memory_data)
            return

    # Add new memory
    memory_data["memories"].append({
        "content": summary,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_memory(memory_data)

def get_memory_context():
    """Get memory context formatted for the LLM"""
    memory_data = load_memory()
    if not memory_data["memories"]:
        return ""

    # Format memories into a context string
    memory_context = MEMORY_CONTEXT_TEMPLATE
    for i, memory in enumerate(memory_data["memories"]):
        memory_context += f"Memory {i+1} ({memory['timestamp']}): {memory['content']}\n\n"

    return memory_context

def display_memory():
    """Display memory in a formatted way"""
    memory_data = load_memory()
    if not memory_data["memories"]:
        return NO_MEMORIES_TEXT

    memory_text = "# Bluey's Memories 🐾\n\n"
    for i, memory in enumerate(memory_data["memories"]):
        memory_text += f"### Memory {i+1}\n"
        memory_text += f"*Saved on: {memory['timestamp']}*\n\n"
        memory_text += f"{memory['content']}\n\n"
        memory_text += "---\n\n"

    return memory_text

def chat(message, history, debug_output=None):
    debug_logs = []

    # Convert gradio history to LangChain message format
    messages = []

    # Get memory context
    memory_context = get_memory_context()
    if memory_context:
        if DEBUG_MODE:
            debug_logs.append(f"**Memory Context**\n{memory_context}")

    # Build system prompt with memory context if available
    system_prompt = SYSTEM_PROMPT
    if memory_context:
        system_prompt += f"\n\n{memory_context}{MEMORY_USAGE_INSTRUCTION}"

    # Add system message first
    messages.append(SystemMessage(content=system_prompt))

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

def clear_and_save_memory(history):
    """Clear chat history and save memory"""
    if history:
        # Summarize conversation
        summary = summarize_conversation(history)
        if summary:
            add_to_memory(summary)

    # Display updated memory
    memory_text = display_memory()

    return [], DEFAULT_DEBUG_TEXT, memory_text

def initialize_memory_file():
    """Initialize memory file if it doesn't exist"""
    if not os.path.exists(MEMORY_FILE):
        save_memory({"memories": []})
        print(f"Created new memory file at {os.path.abspath(MEMORY_FILE)}")
    else:
        print(f"Using existing memory file at {os.path.abspath(MEMORY_FILE)}")

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
                    avatar_images=(os.path.join(ASSETS_FOLDER, "human.png"), os.path.join(ASSETS_FOLDER, "blueybot.png")),
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

        # Connect the interface components
        msg.submit(user, [msg, chatbot, debug_output], [msg, chatbot, debug_output]).then(
            bot, [chatbot, debug_output], [chatbot, debug_output]
        )

        clear.click(clear_and_save_memory, [chatbot], [chatbot, debug_output, memory_display])
        save_mem.click(clear_and_save_memory, [chatbot], [chatbot, debug_output, memory_display])
        refresh_memory.click(display_memory, [], [memory_display])

        # Initialize memory display
        demo.load(display_memory, [], [memory_display])
else:
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
            bubble_full_width=False,
            avatar_images=(os.path.join(ASSETS_FOLDER, "human.png"), os.path.join(ASSETS_FOLDER, "blueybot.png")),
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

# Call this function before launching the demo
initialize_memory_file()

# Then launch the demo
demo.launch()

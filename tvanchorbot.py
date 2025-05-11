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
MEMORY_FILE = "chatbot_memory.json"  # File to store memory

# Constants for repeated strings
CHATBOT_TITLE = "Republic TV - Goswami Bot"
CHATBOT_DESCRIPTION = "This chatbot maintains conversation context and searches for information when it does not know and Talks like our Anchor Arnab Goswami"
DEFAULT_DEBUG_TEXT = "Debug information will appear here"
DEFAULT_MEMORY_TEXT = "Memory will be displayed here"
NO_MEMORIES_TEXT = "No memories stored yet."
SEARCH_TRIGGER_PHRASE = "I need to search for this information"

# Base system prompt that doesn't change
BASE_SYSTEM_PROMPT = (
    "You are an assistant who talks like Arnab Goswami and use his style in your response. Your name is Goswami Bot. If you don't know the answer to a question, "
    f"say '{SEARCH_TRIGGER_PHRASE}' and I'll search for you. "
    "When search results are provided, use them to inform your response, but "
    "don't explicitly mention that you're using search results but just say part of your response As the nation says.."
)

# Memory context template
MEMORY_CONTEXT_TEMPLATE = "Here are some relevant memories from previous conversations:\n\n"
MEMORY_USAGE_INSTRUCTION = "\n\nUse this memory information when relevant to the conversation."

# Search context template
SEARCH_CONTEXT_TEMPLATE = "Search results for '{}':\n{}\n\nPlease answer the user's question using these search results when relevant."

llm_groq = ChatGroq(model_name=GROQ_MODEL_NAME, api_key=GROQ_API_KEY)

import gradio as gr


def search_ddg(query, max_results=3):
    """Search DuckDuckGo and return results"""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
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

# Constants for summarization
SUMMARIZE_SYSTEM_PROMPT = "You are a helpful assistant. Summarize the following conversation into a concise paragraph capturing the key information and facts discussed. Focus only on factual information that would be useful to remember for future conversations."
SUMMARIZE_HUMAN_PROMPT_TEMPLATE = "Here's the conversation to summarize:\n\n{}"
SUMMARIZE_ERROR_TEMPLATE = "Conversation on {} (failed to summarize)"

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

    # Get summary from LLM
    try:
        summary = llm_groq.invoke(summarize_prompt).content
        return summary
    except Exception as e:
        print(f"Error summarizing conversation: {e}")
        return SUMMARIZE_ERROR_TEMPLATE.format(datetime.now().strftime('%Y-%m-%d %H:%M'))

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

def add_debug_log(debug_logs, message):
    """Helper function to add debug logs if debug mode is enabled"""
    if DEBUG_MODE:
        debug_logs.append(message)
    return debug_logs

def chat(message, history, debug_output=None):
    debug_logs = []

    # Convert gradio history to LangChain message format
    messages = []

    # Get memory context
    memory_context = get_memory_context()
    if memory_context:
        add_debug_log(debug_logs, f"**Memory Context**\n{memory_context}")

    # Build system prompt with memory context if available
    system_prompt = BASE_SYSTEM_PROMPT
    if memory_context:
        system_prompt += f"\n\n{memory_context}{MEMORY_USAGE_INSTRUCTION}"

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

    # Log initial messages
    add_debug_log(debug_logs, format_messages(messages, "Initial Messages"))

    # First, try to answer without search
    initial_response = llm_groq.invoke(messages).content
    add_debug_log(debug_logs, f"**Initial Response**\n{initial_response}")

    # Check if the model indicates it needs to search
    if SEARCH_TRIGGER_PHRASE in initial_response:
        add_debug_log(debug_logs, f"**Performing Search**\n- Query: \"{message}\"\n- Max Results: 3\n- Search Provider: DuckDuckGo")

        # Perform search
        search_results = search_ddg(message)

        # Format search results for debug display
        if DEBUG_MODE:
            if not search_results or (len(search_results) == 1 and search_results[0].startswith("[")):
                # Error occurred
                add_debug_log(debug_logs, f"**Search Results**\n{search_results[0] if search_results else 'No results returned'}")
            else:
                # Format successful results
                results_formatted = []
                for i, result in enumerate(search_results):
                    results_formatted.append(f"**Source {i+1}:**\n```\n{result}\n```")
                add_debug_log(debug_logs, f"**Search Results** (Found {len(search_results)} results)\n\n" + "\n\n".join(results_formatted))

        # Create search context for the model
        search_context = "\n\n".join([f"Source {i+1}: {result}" for i, result in enumerate(search_results)])

        # Create new message list with search results
        search_messages = messages.copy()
        search_messages.append(AIMessage(content=SEARCH_TRIGGER_PHRASE))
        search_messages.append(SystemMessage(content=SEARCH_CONTEXT_TEMPLATE.format(message, search_context)))

        # Log search messages
        add_debug_log(debug_logs, format_messages(search_messages, "Messages With Search Results"))

        # Get final response with search results
        final_response = llm_groq.invoke(search_messages).content
        add_debug_log(debug_logs, f"**Final Response**\n{final_response}")

        response = final_response
    else:
        # If no search needed, use the initial response
        response = initial_response

    # Update debug output if needed and return response
    if DEBUG_MODE and debug_output is not None:
        debug_output = "\n\n".join(debug_logs)
        return response, debug_output
    return response

def display_memory():
    """Display memory in a formatted way"""
    memory_data = load_memory()
    if not memory_data["memories"]:
        return NO_MEMORIES_TEXT

    memory_text = "# Stored Memories\n\n"
    for i, memory in enumerate(memory_data["memories"]):
        memory_text += f"### Memory {i+1}\n"
        memory_text += f"*Saved on: {memory['timestamp']}*\n\n"
        memory_text += f"{memory['content']}\n\n"
        memory_text += "---\n\n"

    return memory_text

def user(user_message, history, debug=None):
    """Process user message and update history"""
    return "", history + [{"role": "user", "content": user_message}], debug

def bot(history, debug=None):
    """Process bot response based on user message"""
    user_message = history[-1]["content"]
    if debug is not None:
        response, new_debug = chat(user_message, history[:-1], debug)
        history.append({"role": "assistant", "content": response})
        return history, new_debug
    else:
        response = chat(user_message, history[:-1])
        history.append({"role": "assistant", "content": response})
        return history

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

# Create the appropriate interface based on debug mode
if DEBUG_MODE:
    with gr.Blocks() as demo:
        gr.Markdown(f"<h1 style='font-size: 2.5em; font-weight: bold; margin-bottom: 0.5em;'>{CHATBOT_TITLE}</h1>")
        gr.Markdown(CHATBOT_DESCRIPTION)

        with gr.Tabs():
            with gr.TabItem("Chat"):
                chatbot = gr.Chatbot(type="messages")
                msg = gr.Textbox(placeholder="Type your message here...", show_label=False)
                with gr.Row():
                    clear = gr.Button("Clear & Save Memory")
                    new_chat = gr.Button("New Chat")

            with gr.TabItem("Debug Info"):
                debug_output = gr.Markdown(DEFAULT_DEBUG_TEXT)

            with gr.TabItem("Memory"):
                memory_display = gr.Markdown(DEFAULT_MEMORY_TEXT)
                refresh_memory = gr.Button("Refresh Memory")

        # Connect the interface components
        msg.submit(user, [msg, chatbot, debug_output], [msg, chatbot, debug_output]).then(
            bot, [chatbot, debug_output], [chatbot, debug_output]
        )

        clear.click(clear_and_save_memory, [chatbot], [chatbot, debug_output, memory_display])
        new_chat.click(clear_and_save_memory, [chatbot], [chatbot, debug_output, memory_display])
        refresh_memory.click(display_memory, [], [memory_display])

        # Initialize memory display
        demo.load(display_memory, [], [memory_display])
else:
    # Simple interface without debug information
    def simple_chat(message, history):
        return chat(message, history)

    demo = gr.ChatInterface(
        fn=simple_chat,
        title=CHATBOT_TITLE,
        description=CHATBOT_DESCRIPTION,
    )

def initialize_memory_file():
    """Initialize memory file if it doesn't exist"""
    if not os.path.exists(MEMORY_FILE):
        save_memory({"memories": []})
        print(f"Created new memory file at {os.path.abspath(MEMORY_FILE)}")
    else:
        print(f"Using existing memory file at {os.path.abspath(MEMORY_FILE)}")

# Call this function before launching the demo
initialize_memory_file()

# Then launch the demo
demo.launch(debug=DEBUG_MODE)

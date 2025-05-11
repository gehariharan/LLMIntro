from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import GROQ_API_KEY, GROQ_MODEL_NAME
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException

# Configuration
DEBUG_MODE = True  # Set to False to disable debug information

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

def chat(message, history, debug_output=None):
    debug_logs = []
    
    # Convert gradio history to LangChain message format
    messages = []
    
    # Add system message first
    system_prompt = (
        "You are an assistant who talks like Arnab Goswami and use his style in your response. If you don't know the answer to a question, "
        "say 'I need to search for this information' and I'll search for you. "
        "When search results are provided, use them to inform your response, but "
        "don't explicitly mention that you're using search results but just say part of your response As the nation says.."
    )
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
    if "I need to search for this information" in initial_response:
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
        search_messages.append(AIMessage(content="I need to search for this information"))
        search_messages.append(SystemMessage(content=f"Search results for '{message}':\n{search_context}\n\nPlease answer the user's question using these search results when relevant."))
        
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
    with gr.Blocks() as demo:
        gr.Markdown("<h1 style='font-size: 2.5em; font-weight: bold; margin-bottom: 0.5em;'>Republic TV Chatbot</h1>")
        gr.Markdown("This chatbot maintains conversation context and searches for information when it does not know and Talks like Arnab Goswami")
        
        with gr.Tabs():
            with gr.TabItem("Chat"):
                chatbot = gr.Chatbot(type="messages")
                msg = gr.Textbox(placeholder="Type your message here...", show_label=False)
                clear = gr.Button("Clear")
            
            with gr.TabItem("Debug Info"):
                debug_output = gr.Markdown("Debug information will appear here")
        
        def user(user_message, history, debug):
            return "", history + [{"role": "user", "content": user_message}], debug
        
        def bot(history, debug):
            user_message = history[-1]["content"]
            response, new_debug = chat(user_message, history[:-1], debug)
            history.append({"role": "assistant", "content": response})
            return history, new_debug
        
        def clear_all():
            return [], "Debug information will appear here"
        
        msg.submit(user, [msg, chatbot, debug_output], [msg, chatbot, debug_output]).then(
            bot, [chatbot, debug_output], [chatbot, debug_output]
        )
        
        clear.click(clear_all, None, [chatbot, debug_output])
else:
    # Simple interface without debug information
    def simple_chat(message, history):
        return chat(message, history)
    
    demo = gr.ChatInterface(
        fn=simple_chat,
        title="Republic TV Chatbot",
        description="This chatbot maintains conversation context and searches for information when it does not know and Talks like Arnab Goswami",
    )

demo.launch()

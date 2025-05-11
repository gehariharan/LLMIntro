# LLMIntro: Building Advanced Chatbots with LLMs

This repository contains a collection of chatbot implementations using Large Language Models (LLMs), with a focus on practical applications and advanced features like web search integration and conversation memory.

![Republic TV Chatbot](https://img.shields.io/badge/Chatbot-Republic%20TV%20Style-red)
![LangChain](https://img.shields.io/badge/Framework-LangChain-blue)
![Groq](https://img.shields.io/badge/LLM-Groq-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

- **Conversational AI**: Natural language interactions with context awareness
- **Web Search Integration**: Automatic web search when the chatbot doesn't know an answer
- **Memory System**: Long-term memory to remember previous conversations
- **Custom Personality**: Chatbot with the speaking style of Arnab Goswami (Indian news anchor)
- **Debug Mode**: Detailed view of what's happening behind the scenes
- **User-friendly Interface**: Built with Gradio for easy interaction

## 📋 Project Structure

### Main Components
- `chatbotwithSearch.py`: Main implementation with search and memory capabilities
- `chatbotwithSearch&memory.py`: Alternative implementation with memory features
- `config.py`: Configuration file for API keys and model settings
- `chatbot_memory.json`: File that stores conversation memories

### Additional Scripts
- `gradiochatbot.py`: Simple Gradio-based chatbot implementation
- `newsreaderllm.py`: Script for reading and summarizing news articles using LLMs
- `nexttokenpredict.py`: Demonstrates next token prediction capabilities
- `tokenizer.py`: Implementation of tokenization concepts for LLMs
- `tokenprediction.py`: Advanced token prediction and analysis

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Groq API key (for LLM access)
- Internet connection (for web search functionality)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/LLMIntro.git
   cd LLMIntro
   ```

2. Install required packages:
   ```bash
   pip install langchain langchain-groq gradio duckduckgo-search
   ```

3. Create a `config.py` file with your API keys:
   ```python
   GROQ_API_KEY = "your_groq_api_key_here"
   GROQ_MODEL_NAME = "llama3-70b-8192"  # or your preferred model
   ```

### Running the Scripts

#### Main Chatbot with Search and Memory
```bash
python chatbotwithSearch.py
```

#### Alternative Chatbot Implementation
```bash
python "chatbotwithSearch&memory.py"
```

#### Simple Gradio Chatbot
```bash
python gradiochatbot.py
```

#### News Reader
```bash
python newsreaderllm.py
```

#### Token Prediction Demos
```bash
python nexttokenpredict.py
python tokenprediction.py
```

#### Tokenizer Demo
```bash
python tokenizer.py
```

Each script will start a Gradio web interface (where applicable), typically accessible at http://127.0.0.1:7860 in your browser.

## 💡 How It Works

### Core Components

1. **LLM Integration**: Uses LangChain with Groq to access powerful language models
2. **Web Search**: Integrates DuckDuckGo search when the chatbot needs additional information
3. **Memory System**: Summarizes and stores conversation history for future reference
4. **Gradio Interface**: Provides an intuitive web interface with different modes

### Conversation Flow

1. User sends a message through the interface
2. The chatbot processes the message with context from previous conversation
3. If the chatbot can answer directly, it responds in Arnab Goswami's style
4. If the chatbot needs more information, it performs a web search and uses the results to inform its response
5. Conversations can be summarized and stored in memory for future reference

## 🔧 Customization

### Changing the Chatbot Personality

Modify the `BASE_SYSTEM_PROMPT` constant in `chatbotwithSearch.py` to change the chatbot's personality and behavior.

### Disabling Debug Mode

Set `DEBUG_MODE = False` at the top of `chatbotwithSearch.py` to use the simplified interface without debug information.

### Adjusting Memory Settings

The memory system can be customized by modifying the memory-related functions and constants in the code.

## 📝 Example Usage

1. **Basic Questions**: Ask general knowledge questions and get responses in Arnab Goswami's style
2. **Current Events**: Ask about recent news (the chatbot will search for up-to-date information)
3. **Follow-up Questions**: The chatbot maintains context, so you can ask follow-up questions
4. **Memory Recall**: After clearing a conversation, the chatbot can still recall key information from previous chats

## 🔍 Debug Mode Features

When `DEBUG_MODE = True`, the interface includes:

- **Chat Tab**: The main conversation interface
- **Debug Info Tab**: Shows detailed information about:
  - Initial messages sent to the LLM
  - The LLM's initial response
  - Search queries and results (when applicable)
  - Final response generation
- **Memory Tab**: Displays stored memories from previous conversations

## 🧪 Exploring Other Scripts

This repository includes several scripts that demonstrate different aspects of working with LLMs:

### `gradiochatbot.py`
A simple chatbot implementation using Gradio and LangChain. This is a good starting point to understand the basics of building a conversational interface.

### `newsreaderllm.py`
Demonstrates how to use LLMs to read and summarize news articles. This script shows how to process external content and generate summaries.

### `tokenizer.py`
Explores the concept of tokenization, which is fundamental to how LLMs process text. This script shows how text is converted into tokens that the model can understand.

### `nexttokenpredict.py` and `tokenprediction.py`
These scripts demonstrate token prediction capabilities, showing how LLMs predict the next tokens in a sequence. This helps understand the underlying mechanics of text generation.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the LLM framework
- [Groq](https://groq.com/) for the LLM API
- [Gradio](https://gradio.app/) for the web interface
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) for web search capabilities

---

Created with ❤️ as part of the LLMIntro project

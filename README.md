# LLMIntro: Building Advanced Chatbots with LLMs

This repository contains a collection of chatbot implementations using Large Language Models (LLMs), with a focus on practical applications and advanced features like web search integration and conversation memory.

![Republic TV Chatbot](https://img.shields.io/badge/Chatbot-Republic%20TV%20Style-red)
![Bluey Chatbot](https://img.shields.io/badge/Chatbot-Bluey%20Style-blue)
![LangChain](https://img.shields.io/badge/Framework-LangChain-blue)
![Groq](https://img.shields.io/badge/LLM-Groq-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

- **Conversational AI**: Natural language interactions with context awareness
- **Web Search Integration**: Automatic web search when the chatbot doesn't know an answer
- **Memory System**: Long-term memory to remember previous conversations
- **Custom Personalities**:
  - Republic TV style chatbot with Arnab Goswami's speaking style
  - Child-friendly Bluey chatbot with playful, imaginative responses
- **Debug Mode**: Detailed view of what's happening behind the scenes
- **User-friendly Interface**: Built with Gradio for easy interaction

## 📋 Project Structure

### Main Components
- `tvanchorbot.py`: Republic TV style chatbot with search and memory capabilities
- `bluebot.py`: Bluey-themed chatbot for children with search and memory
- `config.py.template`: Template for configuration file (copy to config.py and add your API keys)
- `chatbot_memory.json`: File that stores Republic TV chatbot memories
- `bluey_memory.json`: File that stores Bluey chatbot memories

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
   pip install langchain langchain-groq gradio duckduckgo-search python-dotenv
   ```

3. Set up your configuration (choose one method):

   **Option 1: Using config.py (Basic)**
   ```bash
   cp config.py.template config.py
   # Edit config.py with your API keys
   ```

   **Option 2: Using environment variables (More Secure)**
   ```bash
   # Create a .env file with your API keys
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   echo "GROQ_MODEL_NAME=llama3-70b-8192" >> .env
   ```

   ⚠️ **SECURITY WARNING**: Never commit your `config.py` or `.env` files to version control. Both files are included in `.gitignore` to prevent accidental exposure of API keys.

### Running the Scripts

#### Republic TV Style Chatbot
```bash
python tvanchorbot.py
```

#### Bluey Style Chatbot for Children
```bash
python bluebot.py
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
3. If the chatbot can answer directly, it responds in the appropriate style (Arnab Goswami or Bluey)
4. If the chatbot needs more information, it performs a web search and uses the results to inform its response
5. Conversations can be summarized and stored in memory for future reference

## 🔧 Customization

### Changing the Chatbot Personality

- **Republic TV Style**: Modify the `BASE_SYSTEM_PROMPT` constant in `tvanchorbot.py`
- **Bluey Style**: Modify the `SYSTEM_PROMPT` constant in `bluebot.py`

### Disabling Debug Mode

Set `DEBUG_MODE = False` at the top of the respective script to use the simplified interface without debug information.

### Adjusting Memory Settings

The memory system can be customized by modifying the memory-related functions and constants in the code.

### Adding Custom Images

Place images in the `assets` folder to customize the chatbot's appearance. The code will automatically create this folder if it doesn't exist.

## 📝 Example Usage

### Republic TV Style Chatbot
1. **Current Events**: Ask about recent news (the chatbot will search for up-to-date information)
2. **Political Questions**: Get responses in Arnab Goswami's dramatic style
3. **Follow-up Questions**: The chatbot maintains context for natural conversation flow

### Bluey Style Chatbot
1. **Child-Friendly Interactions**: Ask questions suitable for children
2. **Educational Content**: Learn about animals, planets, or other topics in a fun way
3. **Imaginative Play**: Engage in pretend games and creative scenarios

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

## 🔒 Security Best Practices

1. **API Key Protection**:
   - Never commit API keys to version control
   - Use environment variables or a separate config file that's excluded from Git
   - Rotate API keys if they're accidentally exposed

2. **Environment Variables**:
   - Consider using `.env` files with the `python-dotenv` package
   - This approach is more secure than hardcoding keys in your scripts

3. **Child Safety** (for Bluey chatbot):
   - The Bluey chatbot includes child-friendly search modifications
   - Search queries are appended with "for kids" and use safe search settings
   - Responses are designed to be appropriate for children

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
- Bluey character and concept by Ludo Studio

---

Created with ❤️ as part of the LLMIntro project

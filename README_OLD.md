# Artifix Ai

Artifix is an intelligent chat assistant designed to interact with users via text and voice commands. Built using Python, it integrates system monitoring, text-to-speech, speech recognition, and multiple external APIs to respond to user queries.

## Features

- **Text and Voice Interaction**: Users can input queries via text or voice, and Artifix responds either through text or speech.
- **System Information**: Displays real-time system status, including CPU usage, RAM usage, battery percentage, and current time.
- **Wikipedia Integration**: Artifix can retrieve information about people or topics directly from Wikipedia.
- **NLP Integration**: The system can handle a wide range of queries using APIs like Gemini for advanced question answering.
- **Customizable Responses**: Responds to predefined queries (e.g., greetings, battery status) and generates answers based on the user's query.

## Usage

1. **Run the Application**:
   - Make sure you have all the dependencies installed, including `flet`, `pyttsx3`, `speech_recognition`, `psutil`, and `gradio_client`.
   - Set up your API keys for external services like Google Gemini in the `.env` file.
   - Run the main script:
     ```bash
     python main.py
     ```

2. **Interact with Artifix**:
   - You can type a message in the input field or use the microphone button to speak a command.
   - Artifix will process your input and display the response in the chat area. If it's a voice command, it will also speak the response aloud.

3. **Supported Queries**:
   - **Greetings**: "Hello", "Hi", "How are you?"
   - **Time**: "What time is it?"
   - **System Info**: "What is the battery percentage?", "What is my CPU usage?"
   - **Wikipedia**: "Who is [Name]?", "Tell me about [Topic]."
   - **General Queries**: Artifix can handle various types of questions (e.g., "Explain quantum mechanics", "How does a car engine work?") using external APIs.

4. **Voice Commands**:
   - Click the microphone button to speak a command.
   - Artifix will transcribe the voice input, process it, and respond accordingly.

## How It Works

1. **User Input**: Artifix accepts text or voice input.
   - Text input is processed directly.
   - Voice input is converted into text using speech recognition.
   
2. **Query Handling**:
   - The system evaluates the query to determine if it is a request for system information, a Wikipedia search, or a more general query.
   - For specific queries, such as asking for a person’s details, Artifix will fetch the information from Wikipedia.
   - For more complex questions, it uses the Gemini API or LLM (Large Language Model) to generate responses.

3. **Response Output**:
   - Artifix responds with text in the chat window.
   - If configured, it can also speak the response aloud using the text-to-speech engine (`pyttsx3`).

## Requirements

To run this project, you'll need to install the following dependencies:

- `flet` - For building the frontend UI.
- `pyttsx3` - For text-to-speech functionality.
- `speech_recognition` - For voice input functionality.
- `psutil` - For fetching system information.
- `gradio_client` - For communication with external LLMs.
- `google-generativeai` - For integration with the Gemini API (if used).

Additionally, ensure you have the required API keys set up in the `.env` file for external APIs like Gemini.

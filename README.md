# Artifix AI - Advanced Desktop Assistant

Artifix is a comprehensive AI-powered desktop assistant that offers seamless voice-controlled commands with wake word detection, full-duplex conversation, multimodal input (voice, GUI, camera), powerful file and document management including editing and OCR, system control, persistent memory with contextual understanding, integrated communication, robust task/time management, developer-focused automation, and customizable agent modes for personalized workflows.

## 🚀 Key Features

### 🎙️ Voice & Audio
- **Wake Word Detection**: Hands-free activation with customizable wake words ("Hey Artifix", "Artifix")
- **Full-Duplex Conversation**: Continuous listening and natural conversation flow
- **Text-to-Speech**: High-quality voice responses with personality-based settings
- **Multi-language Support**: Translation and language detection capabilities

### 🖥️ System Control
- **Application Management**: Launch, close, and monitor applications
- **Volume Control**: Adjust system volume with voice commands
- **Power Management**: Shutdown, restart, sleep system operations
- **System Monitoring**: Real-time CPU, memory, battery, and disk usage
- **Network Management**: Check connectivity and network information

### 📁 File & Document Management
- **File Operations**: Create, read, write, delete, copy, move files and directories
- **Intelligent Search**: Content-based file search across the system
- **Document Processing**: Text extraction from PDFs and images (OCR ready)
- **File Organization**: Categorization and metadata management

### 🧠 Persistent Memory & Context
- **Conversation History**: Persistent storage of all interactions
- **Context Understanding**: Maintains session context for natural conversations
- **Knowledge Base**: Learns and stores user preferences and information
- **Session Management**: Automatic session tracking and recall

### 💬 Communication Hub
- **Email Integration**: Send and receive emails with attachment support
- **Slack Integration**: Send messages and monitor channels
- **Translation Services**: Real-time text translation between languages
- **Multi-platform Support**: Unified communication interface

### 📅 Task & Time Management
- **Task Management**: Create, track, and complete tasks with priorities
- **Calendar Integration**: Schedule events and manage appointments
- **Smart Reminders**: Time-based and context-aware notifications
- **Productivity Analytics**: Track completion rates and time management

### 👨‍💻 Developer Tools
- **Git Integration**: Status, commit, push, pull operations
- **Code Analysis**: Linting, testing, and building projects
- **Debug Assistance**: Log analysis and error tracking
- **Web Automation**: Browser automation for testing and scraping
- **Performance Profiling**: Code performance analysis

### 📷 Multimodal Input
- **Camera Integration**: Real-time video capture and processing
- **Visual Understanding**: Scene description and object identification
- **Gesture Recognition**: Basic gesture detection for hands-free control
- **Image Processing**: Face detection and visual analysis

### 🎭 Customizable Agent Modes
- **Professional Mode**: Business-focused, formal communication
- **Casual Mode**: Friendly, conversational interactions
- **Technical Mode**: Developer-oriented, detailed technical responses
- **Creative Mode**: Imaginative, inspiring for creative projects
- **Research Mode**: Academic, thorough analysis and citations
- **Personal Mode**: Empathetic, adaptive to user preferences
- **Gaming Mode**: Enthusiastic, gaming-culture aware

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Microphone and speakers/headphones
- Camera (optional, for visual features)
- Internet connection for AI services

### Installation
```bash
# Clone the repository
git clone https://github.com/PrakharDoneria/Artifix.git
cd Artifix

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp api/.env.sample api/.env
# Edit api/.env with your API keys
```

### Configuration
1. **Sarvam AI API**: Add your API key to `api/.env`
2. **Email (Optional)**: Configure email credentials for communication features
3. **Slack (Optional)**: Set up Slack bot token for team communication
4. **Translation (Optional)**: Add Google Translate API key

## 🎯 Usage Examples

### Voice Commands
```
"Hey Artifix, what's my CPU usage?"
"Start camera and describe what you see"
"Add task: Review project proposal"
"Send email to john@example.com"
"Switch to technical mode"
"Show me today's calendar"
"Run git status"
"Take a picture"
```

### System Control
```
"Increase volume"
"Launch Chrome browser" 
"Check battery level"
"Shutdown computer in 5 minutes"
```

### File Management
```
"List files in Documents folder"
"Search for files containing 'budget'"
"Create a new file called notes.txt"
"Read the content of report.pdf"
```

### Task Management
```
"Add reminder: Call client at 3 PM"
"Show my pending tasks"
"Create meeting: Team standup tomorrow at 10 AM"
"What's my schedule for today?"
```

### Developer Features
```
"Run tests for current project"
"Commit changes with message 'Fixed login bug'"
"Lint the Python code"
"Build the project"
```

## 🏗️ Architecture

### Core Modules
- **`core/app.py`**: Main application and conversation management
- **`core/wake_word.py`**: Wake word detection and continuous listening
- **`core/system_control.py`**: System operations and monitoring
- **`core/file_manager.py`**: File and document operations
- **`core/memory_manager.py`**: Persistent memory and context
- **`core/communication.py`**: Email, Slack, and translation services
- **`core/task_manager.py`**: Task, calendar, and reminder management
- **`core/developer_tools.py`**: Git, testing, and development automation
- **`core/camera.py`**: Camera input and visual processing
- **`core/agent_modes.py`**: Personality and mode management

### API Integration
- **`api/sarvam.py`**: Sarvam AI integration for natural language processing
- **`api/wikipedia.py`**: Wikipedia knowledge base integration

### User Interface
- **`ui/layout.py`**: Flet-based GUI with real-time chat interface

## 🎛️ Agent Modes

### Professional Mode
- Formal, business-oriented responses
- Focus on productivity and efficiency
- Ideal for work environments

### Casual Mode  
- Friendly, conversational tone
- Relaxed and personable interactions
- Perfect for daily personal use

### Technical Mode
- Developer-focused responses
- Detailed technical explanations
- Code-aware and precise

### Creative Mode
- Imaginative and inspiring
- Helps with creative projects
- Encourages artistic expression

### Research Mode
- Academic and thorough
- Fact-based responses
- Methodical analysis approach

### Personal Mode
- Learns your preferences
- Empathetic and caring
- Adapts to your needs

### Gaming Mode
- Gaming culture aware
- Enthusiastic about games
- Esports and streaming focused

## 🔧 Advanced Configuration

### Wake Word Customization
```python
# Modify wake words in core/app.py
wake_config = WakeWordConfig(
    wake_words=["hey artifix", "artifix", "computer"],
    sensitivity=0.5,
    enabled=True
)
```

### Voice Settings
```python
# Adjust voice parameters per mode
voice_settings = {
    "rate": 175,      # Speech rate
    "volume": 0.8,    # Volume level
    "voice": "professional"  # Voice type
}
```

### UI Theming
```python
# Customize UI colors per agent mode
ui_theme = {
    "primary": "#1f2937",
    "secondary": "#374151", 
    "accent": "#3b82f6"
}
```

## 🛡️ Privacy & Security

- **Local Processing**: Core functions work offline
- **Encrypted Storage**: Sensitive data is encrypted
- **API Security**: Secure API key management
- **Permission Control**: Granular permission system
- **Data Retention**: Configurable data retention policies

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 core/ api/ ui/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Sarvam AI for natural language processing
- OpenCV for computer vision capabilities
- Flet for the modern UI framework
- The open-source community for various libraries

## 🆘 Support

For support, please:
1. Check the [FAQ](docs/FAQ.md)
2. Search existing [Issues](https://github.com/PrakharDoneria/Artifix/issues)
3. Create a new issue with detailed information

## 🗺️ Roadmap

- [ ] Advanced OCR with multiple languages
- [ ] Smart home device integration
- [ ] Mobile app companion
- [ ] Plugin system for extensions
- [ ] Advanced AI model integration
- [ ] Cloud synchronization
- [ ] Voice training for better recognition
- [ ] Advanced gesture recognition
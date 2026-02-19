# Autonomous Agent Pro

**A powerful, stable, and autonomous AI agent system with complete device control through natural language commands.**

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-22+-green.svg)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-purple.svg)

## Overview

Autonomous Agent Pro is a comprehensive AI agent system that gives you complete control over your device through natural language commands. Built with DeepSeek as the default LLM, it supports multi-language code execution, self-healing capabilities, intelligent auto-continuation with token limit detection, and a modern Manus AI-like GUI.

### Key Capabilities

The agent can execute tasks across multiple domains by understanding your natural language instructions and breaking them down into executable steps. It supports Python, JavaScript, Shell, Java, R, and Ruby code execution with full sandboxing and safety mechanisms. The system includes automatic error detection, self-healing logic, intelligent task state management, and automatic resumption from checkpoints when token limits are reached.

### Architecture

The system is built on a modern stack with a FastAPI backend for robust API handling and a React frontend for an intuitive user interface. Communication between frontend and backend uses WebSocket for real-time streaming responses. The architecture supports horizontal scaling through containerization and includes comprehensive logging, monitoring, and memory management capabilities.

## Features

### Core Capabilities

**Multi-Language Code Execution** - Execute code in Python, JavaScript, Shell, Bash, Java, R, and Ruby with isolated execution environments and timeout protection.

**LLM Integration** - Support for DeepSeek (default), OpenAI GPT-4, Claude, Llama, and Groq with streaming responses and function calling capabilities.

**Autonomous Task Planning** - Automatic decomposition of complex tasks into multi-step workflows with dependency management and execution sequencing.

**Self-Healing Execution** - Automatic error detection and intelligent code correction using LLM analysis of failures.

**Safe Execution** - Comprehensive code validation, sandboxing, and optional user approval before code execution.

**Real-time Streaming** - WebSocket-based streaming responses for immediate feedback during task execution.

### Advanced Features

**Intelligent Auto-Continuation** - Detects token limits and automatically resumes tasks from saved checkpoints with context compression.

**Task State Management** - Persistent tracking of task progress, steps, and execution history with recovery capabilities.

**Memory Management** - Sliding window memory, context compression, and importance scoring for efficient token usage.

**Voice Input** - Hands-free interaction using Whisper API for speech-to-text transcription.

**Computer Vision** - Screen capture and image analysis capabilities for visual task automation.

**Execution History** - Complete tracking of all executed code with results, errors, and performance metrics.

**Session Management** - Persistent conversation history with the ability to resume previous sessions.

**Diagram Generation** - Automatic generation of Mermaid diagrams for task execution plans and system architecture.

**User Approval Mode** - Safe mode requiring explicit user confirmation before executing potentially dangerous operations.

## Quick Start - Single Command Installation

Choose your operating system and run the appropriate command:

### 🐧 Ubuntu / Debian Linux

```bash
git clone https://github.com/Irfan430/AGENT-Pro.git && cd AGENT-Pro && cp .env.example .env && python3 -m pip install -r requirements.txt && cd client && npm install && cd .. && echo "✓ Installation complete! Run: python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
```

### 🔴 Kali Linux

```bash
git clone https://github.com/Irfan430/AGENT-Pro.git && cd AGENT-Pro && cp .env.example .env && sudo apt-get update && sudo apt-get install -y python3-pip nodejs npm && python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt && cd client && npm install && cd .. && echo "✓ Installation complete! Run: python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
```

### 🍎 macOS

```bash
git clone https://github.com/Irfan430/AGENT-Pro.git && cd AGENT-Pro && cp .env.example .env && brew install python@3.11 node && python3.11 -m pip install -r requirements.txt && cd client && npm install && cd .. && echo "✓ Installation complete! Run: python3.11 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
```

### 🪟 Windows (PowerShell)

```powershell
git clone https://github.com/Irfan430/AGENT-Pro.git; cd AGENT-Pro; Copy-Item .env.example .env; python -m pip install --upgrade pip; python -m pip install -r requirements.txt; cd client; npm install; cd ..; Write-Host "✓ Installation complete! Run: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
```

### 🐳 Docker (All Platforms)

```bash
git clone https://github.com/Irfan430/AGENT-Pro.git && cd AGENT-Pro && cp .env.example .env && docker-compose up -d && echo "✓ Agent running at http://localhost:3000"
```

## Quick Start - Running the Application

### 🐧 Ubuntu / Debian Linux

```bash
# Terminal 1: Start Backend
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd client && npm run dev
```

Access at: `http://localhost:5173`

### 🔴 Kali Linux

```bash
# Terminal 1: Start Backend
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd client && npm run dev
```

Access at: `http://localhost:5173`

### 🍎 macOS

```bash
# Terminal 1: Start Backend
python3.11 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd client && npm run dev
```

Access at: `http://localhost:5173`

### 🪟 Windows (PowerShell)

```powershell
# Terminal 1: Start Backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd client; npm run dev
```

Access at: `http://localhost:5173`

### 🐳 Docker (All Platforms)

```bash
docker-compose up
```

Access at: `http://localhost:3000`

## Configuration

### Set Your DeepSeek API Key

Edit the `.env` file and add your API key:

```env
DEEPSEEK_API_KEY=sk-your-api-key-here
DEFAULT_LLM_PROVIDER=deepseek
EXECUTION_MODE=safe
```

Get your API key from: https://platform.deepseek.com

## Usage Examples

### Basic Chat Interaction

```
User: "Create a Python script that calculates the sum of numbers 1 to 100"

Agent: [Generates code] → [Validates] → [Executes] → [Returns result: 5050]
```

### Data Analysis

```
User: "Generate 100 random numbers, calculate mean, median, and standard deviation"

Agent: [Generates code] → [Executes] → [Displays statistics]
```

### Multi-Step Task

```
User: "Create a CSV file with sample data, analyze it, and generate a bar chart"

Agent: [Creates task plan] → [Executes step 1] → [Executes step 2] → [Executes step 3] → [Returns results]
```

### Voice Commands

Click the microphone button in the chat interface and speak your command:

```
User: [Speaks] "Show me the weather forecast for tomorrow"

Agent: [Transcribes] → [Processes] → [Returns response]
```

## API Documentation

### REST Endpoints

**POST /api/chat** - Send a message and get a response

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a Python script that prints hello world",
    "session_id": "session-123",
    "auto_execute": false
  }'
```

**POST /api/execute** - Execute code directly

```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python",
    "timeout": 30
  }'
```

**POST /api/task-plan** - Create a task plan

```bash
curl -X POST http://localhost:8000/api/task-plan \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Analyze data and create visualizations",
    "context": "Using sales data from 2024"
  }'
```

**GET /api/session/{session_id}/history** - Get conversation history

```bash
curl http://localhost:8000/api/session/session-123/history
```

### WebSocket Endpoint

For real-time streaming responses:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/session-123');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Your task here",
    auto_execute: false
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chunk') {
    console.log(data.content); // Streaming response
  }
};
```

## Architecture

### System Components

**Frontend (React)** - Modern web interface with real-time chat, code preview, and execution history. Built with React 19, Tailwind CSS, and shadcn/ui components.

**Backend (FastAPI)** - High-performance async API server handling chat, code execution, and task management.

**LLM Manager** - Unified interface for multiple LLM providers with streaming support and function calling.

**Code Executor** - Sandboxed code execution engine supporting multiple languages with timeout protection.

**Agent Core** - Main orchestration logic handling task planning, execution, and conversation management.

**Continuation Manager** - Intelligent token limit detection and automatic task resumption with checkpoints.

**Task State Engine** - Persistent task tracking with step management and recovery capabilities.

**Memory Manager** - Context compression and memory optimization for efficient token usage.

**Safety Validator** - Code validation and security checking to prevent dangerous operations.

**Vision/Voice Manager** - Screen capture, image analysis, and audio transcription capabilities.

**Diagram Generator** - Automatic visualization of task plans using Mermaid diagrams.

### Data Flow

1. Message is received via REST or WebSocket endpoint
2. LLM processes the message and generates a response
3. Token limit is checked; if exceeded, system resumes from checkpoint
4. Code blocks are extracted and validated
5. If auto-execute is enabled, code is executed in sandbox
6. Results are streamed back to client in real-time
7. Task state is updated and saved
8. Execution history is stored for future reference

## Configuration Guide

### LLM Provider Selection

Change the default LLM provider in `.env`:

```env
# Options: deepseek, openai, claude, llama, groq
DEFAULT_LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
```

### Execution Mode

Configure how code execution is handled:

```env
# Options: safe (requires approval), auto (automatic), sandbox (isolated)
EXECUTION_MODE=safe
EXECUTION_TIMEOUT=300  # 5 minutes
MAX_RETRIES=3
```

### Security Settings

Configure restricted modules and safety features:

```env
SANDBOX_ENABLED=True
RESTRICTED_MODULES=os,sys,subprocess,socket
```

### Continuation Settings

Configure auto-continuation behavior:

```env
MAX_CONTINUATION_ATTEMPTS=5
CONTEXT_COMPRESSION_RATIO=0.3
MEMORY_MAX_TOKENS=4000
```

## Safety and Security

### Code Validation

All code is validated before execution:

- **Syntax checking** - Ensures code is syntactically correct
- **Import restrictions** - Prevents dangerous module imports
- **Pattern detection** - Identifies potentially dangerous operations
- **User approval** - Optional requirement for user confirmation

### Sandboxing

Code execution is isolated through:

- **Process isolation** - Each execution runs in a separate process
- **Timeout protection** - Prevents infinite loops and resource exhaustion
- **Output limiting** - Truncates excessive output to prevent memory issues
- **Environment isolation** - Restricted access to system resources

### Self-Healing

When code fails, the system:

1. Analyzes the error using the LLM
2. Generates corrected code
3. Validates the fix
4. Re-executes automatically
5. Returns results or escalates if unrecoverable

### Auto-Continuation

When token limits are reached:

1. System detects truncation (finish_reason == "length")
2. Current state is saved as checkpoint
3. Context is compressed to fit within limits
4. Task resumes from checkpoint with compressed context
5. Process repeats until task is complete

## Troubleshooting

### Port Already in Use

If port 8000 or 5173 is already in use:

```bash
# Change backend port
python -m uvicorn backend.main:app --port 8001

# Change frontend port
cd client && npm run dev -- --port 5174
```

### API Key Issues

Ensure your `.env` file has the correct API key:

```bash
# Check if .env file exists
cat .env | grep DEEPSEEK_API_KEY
```

### Memory Issues

If experiencing memory issues, adjust settings:

```env
MEMORY_MAX_TOKENS=2000  # Reduce from 4000
CONTEXT_COMPRESSION_RATIO=0.2  # Increase compression
```

### WebSocket Connection Issues

Check that your firewall allows WebSocket connections on port 8000.

## Performance Optimization

### For Production

Use Gunicorn instead of uvicorn:

```bash
pip install gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Database Optimization

Enable query caching:

```env
REDIS_ENABLED=True
REDIS_URL=redis://localhost:6379
```

### Memory Optimization

Adjust memory settings for your system:

```env
MEMORY_MAX_TOKENS=2000
SLIDING_WINDOW_SIZE=3
CHECKPOINT_CLEANUP_INTERVAL=3600
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on GitHub
3. Check existing issues for similar problems

## Author

**IRFAN** - Principal AI Systems Architect

## Acknowledgments

- DeepSeek for the powerful LLM API
- Open Interpreter for inspiration on code execution
- Manus AI for UI/UX design inspiration
- The open-source community for various libraries and tools

## Roadmap

- [ ] Multi-agent collaboration system
- [ ] Advanced workflow automation
- [ ] Custom skill development framework
- [ ] Real-time collaboration features
- [ ] Advanced analytics and insights
- [ ] Mobile app support
- [ ] Cloud deployment templates

## Changelog

### v2.0.0 (Current)
- Added DeepSeek API integration
- Implemented intelligent auto-continuation system
- Added task state engine with checkpoint recovery
- Implemented memory management and context compression
- Enhanced error handling and self-healing logic
- Added comprehensive test suite

### v1.0.0
- Initial release
- Multi-language code execution
- Manus AI-like GUI
- Docker support
- Voice input integration
- Computer vision capabilities

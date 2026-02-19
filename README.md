# Autonomous Agent Pro

**A powerful, stable, and autonomous AI agent system with complete device control through natural language commands.**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-22+-green.svg)

## Overview

Autonomous Agent Pro is a comprehensive AI agent system that gives you complete control over your device through natural language commands. Built with DeepSeek as the default LLM, it supports multi-language code execution, self-healing capabilities, and a modern Manus AI-like GUI.

### Key Capabilities

The agent can execute tasks across multiple domains by understanding your natural language instructions and breaking them down into executable steps. It supports Python, JavaScript, Shell, Java, R, and Ruby code execution with full sandboxing and safety mechanisms. The system includes automatic error detection and self-healing logic that can fix code issues without user intervention.

### Architecture

The system is built on a modern stack with a FastAPI backend for robust API handling and a React frontend for an intuitive user interface. Communication between frontend and backend uses WebSocket for real-time streaming responses. The architecture supports horizontal scaling through containerization and includes comprehensive logging and monitoring capabilities.

## Features

### Core Capabilities

**Multi-Language Code Execution** - Execute code in Python, JavaScript, Shell, Bash, Java, R, and Ruby with isolated execution environments and timeout protection.

**LLM Integration** - Support for DeepSeek (default), OpenAI GPT-4, Claude, Llama, and Groq with streaming responses and function calling capabilities.

**Autonomous Task Planning** - Automatic decomposition of complex tasks into multi-step workflows with dependency management and execution sequencing.

**Self-Healing Execution** - Automatic error detection and intelligent code correction using LLM analysis of failures.

**Safe Execution** - Comprehensive code validation, sandboxing, and optional user approval before code execution.

**Real-time Streaming** - WebSocket-based streaming responses for immediate feedback during task execution.

### Advanced Features

**Voice Input** - Hands-free interaction using Whisper API for speech-to-text transcription.

**Computer Vision** - Screen capture and image analysis capabilities for visual task automation.

**Execution History** - Complete tracking of all executed code with results, errors, and performance metrics.

**Session Management** - Persistent conversation history with the ability to resume previous sessions.

**Diagram Generation** - Automatic generation of Mermaid diagrams for task execution plans and system architecture.

**User Approval Mode** - Safe mode requiring explicit user confirmation before executing potentially dangerous operations.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 22 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- DeepSeek API key (or alternative LLM provider)

### Installation

#### Option 1: Local Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/Irfan430/autonomous-agent-pro.git
cd autonomous-agent-pro

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd client
pnpm install
cd ..
```

#### Option 2: Docker Deployment

Build and run using Docker Compose:

```bash
docker-compose up -d
```

This will start the backend API, frontend, MySQL database, and Redis cache.

### Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` to add your API keys and configuration:

```env
DEEPSEEK_API_KEY=your_api_key_here
DEFAULT_LLM_PROVIDER=deepseek
EXECUTION_MODE=safe
```

### Running the Application

#### Local Development

Start the backend server:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal, start the frontend:

```bash
cd client
pnpm dev
```

Access the application at `http://localhost:5173`

#### Docker

```bash
docker-compose up
```

Access at `http://localhost:3000`

## Usage

### Basic Chat Interaction

The simplest way to use the agent is through the chat interface:

```
User: "Create a Python script that analyzes a CSV file and generates a bar chart"

Agent: [Generates code, executes it, returns results]
```

### Code Execution

The agent automatically detects code blocks in responses and can execute them:

```
User: "Write Python code to fetch data from an API and process it"

Agent: [Generates code] → [Validates code] → [Executes code] → [Returns output]
```

### Task Planning

For complex tasks, the agent creates a multi-step plan:

```
User: "Analyze sales data, create visualizations, and generate a report"

Agent: [Creates task plan] → [Executes steps] → [Aggregates results]
```

### Voice Input

Use the microphone button in the chat interface to give voice commands:

```
User: [Speaks] "Show me the weather forecast"

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

The system consists of several interconnected components working together to provide autonomous task execution:

**Frontend (React)** - Modern web interface with real-time chat, code preview, and execution history. Built with React 19, Tailwind CSS, and shadcn/ui components for a polished user experience.

**Backend (FastAPI)** - High-performance async API server handling chat, code execution, and task management. Provides both REST and WebSocket endpoints for flexible client integration.

**LLM Manager** - Unified interface for multiple LLM providers with streaming support, function calling, and error analysis capabilities.

**Code Executor** - Sandboxed code execution engine supporting multiple languages with timeout protection and resource limits.

**Agent Core** - Main orchestration logic handling task planning, execution, self-healing, and conversation management.

**Safety Validator** - Code validation and security checking to prevent dangerous operations.

**Vision/Voice Manager** - Screen capture, image analysis, and audio transcription capabilities.

**Diagram Generator** - Automatic visualization of task plans and execution flows using Mermaid diagrams.

### Data Flow

When a user sends a message, the system follows this flow:

1. Message is received via REST or WebSocket endpoint
2. LLM processes the message and generates a response
3. Code blocks are extracted and validated
4. If auto-execute is enabled, code is executed in sandbox
5. Results are streamed back to client in real-time
6. Execution history is stored for future reference
7. Session state is maintained for conversation continuity

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

### Database Configuration

For production deployments, configure MySQL:

```env
DATABASE_URL=mysql+pymysql://user:password@host:3306/database
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
2. Suggests corrections automatically
3. Retries with corrected code
4. Tracks retry attempts and success rates

## Docker Deployment

### Building the Image

```bash
docker build -t autonomous-agent-pro:latest .
```

### Running with Docker Compose

```bash
docker-compose up -d
```

This starts:
- Backend API (port 8000)
- Frontend (port 3000)
- MySQL database
- Redis cache

### Environment Variables

Configure via `.env` file or Docker environment:

```bash
docker-compose up -d \
  -e DEEPSEEK_API_KEY=your_key \
  -e EXECUTION_MODE=safe
```

## Development

### Project Structure

```
autonomous-agent-pro/
├── backend/                 # Python backend
│   ├── agent/              # Agent core logic
│   ├── executor/           # Code execution
│   ├── llm/                # LLM integration
│   ├── safety/             # Code validation
│   ├── utils/              # Utilities
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI app
├── client/                  # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # UI components
│   │   └── App.tsx         # Main app
│   └── package.json
├── Dockerfile              # Container image
├── docker-compose.yml      # Multi-service setup
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Adding New Features

To add a new feature:

1. Create the backend logic in `backend/`
2. Add API endpoints in `backend/main.py`
3. Create React components in `client/src/`
4. Wire components to API via tRPC hooks
5. Add tests for the new functionality
6. Update documentation

### Testing

Run tests with pytest:

```bash
pytest backend/ -v
```

## Troubleshooting

### Connection Issues

If the frontend cannot connect to the backend:

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `.env`
3. Verify WebSocket URL in frontend configuration

### Code Execution Failures

If code execution fails:

1. Check execution logs in `logs/agent.log`
2. Verify language is supported
3. Check for restricted module imports
4. Review error message for details

### Database Connection

If database connection fails:

1. Verify MySQL is running
2. Check DATABASE_URL in `.env`
3. Verify credentials are correct
4. Check network connectivity

## Performance Optimization

### Caching

Redis is used for caching:

```env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600  # 1 hour
```

### Database Optimization

For production:

1. Create indexes on frequently queried columns
2. Enable query caching
3. Use connection pooling
4. Monitor slow queries

### API Rate Limiting

Implement rate limiting for production:

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.util import get_remote_address

FastAPILimiter.init(redis_client)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**IRFAN** - Original author and maintainer

## Acknowledgments

This project is inspired by Open Interpreter and builds upon its concepts with significant enhancements for stability, safety, and autonomous execution capabilities.

## Support

For issues, questions, or suggestions:

1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Contact the maintainer

## Roadmap

### Upcoming Features

- **Multi-agent collaboration** - Multiple agents working together on complex tasks
- **Advanced scheduling** - Scheduled task execution and cron jobs
- **Custom tools** - User-defined tools and integrations
- **Advanced analytics** - Detailed execution analytics and performance metrics
- **Mobile app** - Native mobile application for iOS and Android
- **Cloud deployment** - One-click deployment to cloud platforms

## References

This project integrates with several external services and libraries:

- DeepSeek API for language model capabilities
- OpenAI API for alternative LLM support
- Anthropic Claude for advanced reasoning
- Whisper API for speech-to-text
- FastAPI for backend framework
- React for frontend framework

---

**Autonomous Agent Pro** - Empowering users with autonomous AI capabilities for complete device control.

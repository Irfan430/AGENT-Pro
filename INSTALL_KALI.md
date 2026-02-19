# AGENT-Pro Installation Guide for Kali Linux

This guide provides step-by-step instructions to install and run AGENT-Pro on Kali Linux without dependency conflicts.

## Prerequisites

- Kali Linux (or any Debian-based Linux)
- Internet connection
- Terminal access

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/Irfan430/AGENT-Pro.git
cd AGENT-Pro
```

### Step 2: Update System Packages

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 3: Install System Dependencies

```bash
sudo apt-get install -y \
  python3 \
  python3-pip \
  python3-dev \
  python3-venv \
  nodejs \
  npm \
  git \
  build-essential \
  libssl-dev \
  libffi-dev \
  libpq-dev \
  curl \
  wget
```

### Step 4: Create a Python Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Upgrade pip and Install Python Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 6: Install Node.js Dependencies

```bash
npm install --legacy-peer-deps
```

Or if you prefer using pnpm:

```bash
npm install -g pnpm
pnpm install
```

### Step 7: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your DeepSeek API key:

```env
DEEPSEEK_API_KEY=sk-your-api-key-here
DEFAULT_LLM_PROVIDER=deepseek
EXECUTION_MODE=safe
```

## Running the Application

### Option 1: Local Development (Two Terminals)

**Terminal 1 - Start Backend:**

```bash
# Make sure your virtual environment is activated
source venv/bin/activate
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**

```bash
cd client
npm run dev
```

Access the application at: `http://localhost:5173`

### Option 2: Docker (Single Command)

```bash
docker-compose up -d
```

Access at: `http://localhost:3000`

## Troubleshooting

### Issue: "pip's dependency resolver does not currently take into account all the packages"

**Solution:** This is a warning, not an error. The application will still work. If you want to avoid it:

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Issue: npm ERESOLVE unable to resolve dependency tree

**Solution:** Use the `--legacy-peer-deps` flag:

```bash
npm install --legacy-peer-deps
npm run dev -- --legacy-peer-deps
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:** Make sure your virtual environment is activated:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Port 8000 or 5173 already in use

**Solution:** Use different ports:

```bash
# Backend on port 8001
python3 -m uvicorn backend.main:app --port 8001

# Frontend on port 5174
cd client && npm run dev -- --port 5174
```

### Issue: "Permission denied" when running commands

**Solution:** Add execute permission:

```bash
chmod +x backend/main.py
```

## Verifying Installation

After installation, verify that everything is working:

```bash
# Check Python packages
python3 -c "import fastapi, pydantic, openai; print('✓ Python packages OK')"

# Check Node.js packages
npm list react vite

# Check backend can start
python3 -m uvicorn backend.main:app --help
```

## Getting Started

1. Open your browser to `http://localhost:5173`
2. Click "Start Using Agent Pro"
3. Type a command like: "Create a Python script that prints hello world"
4. The agent will generate and execute the code

## Next Steps

- Read the main [README.md](README.md) for detailed documentation
- Check [API Documentation](README.md#api-documentation) for API endpoints
- Review [Configuration Guide](README.md#configuration-guide) for advanced settings

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review the main README.md
3. Check the logs in `.manus-logs/` directory
4. Open an issue on GitHub

## Virtual Environment Reminder

Always remember to activate the virtual environment before working:

```bash
source venv/bin/activate
```

To deactivate:

```bash
deactivate
```

---

**Happy coding with AGENT-Pro!** 🚀

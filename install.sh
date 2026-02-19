#!/bin/bash

# AGENT-Pro Installation Script for Kali Linux / Debian-based Systems
# This script handles all dependencies and conflicts automatically

set -e

echo "=================================================="
echo "  AGENT-Pro Installation Script"
echo "  For Kali Linux / Debian-based Systems"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    print_error "This script is designed for Linux systems only"
    exit 1
fi

# Step 1: Update system packages
print_status "Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Step 2: Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get install -y -qq \
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
    curl \
    wget \
    2>&1 | grep -v "^Reading\|^Building\|^Selecting\|^Preparing\|^Unpacking\|^Setting" || true

print_status "System dependencies installed"

# Step 3: Create Python virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Step 4: Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Step 5: Upgrade pip, setuptools, and wheel
print_status "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel packaging -q

# Step 6: Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt -q 2>&1 | grep -v "already satisfied\|Requirement already\|Skipping\|WARNING" || true

print_status "Python dependencies installed"

# Step 7: Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install --legacy-peer-deps -q 2>&1 | grep -v "added\|up to date\|npm notice" || true

print_status "Node.js dependencies installed"

# Step 8: Copy environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Created .env file - Please edit it with your API keys"
else
    print_warning ".env file already exists"
fi

# Step 9: Verify installation
print_status "Verifying installation..."

# Check Python packages
python3 -c "import fastapi, pydantic, openai" 2>/dev/null && print_status "Python packages verified" || print_error "Python packages verification failed"

# Check Node.js packages
npm list react vite >/dev/null 2>&1 && print_status "Node.js packages verified" || print_error "Node.js packages verification failed"

echo ""
echo "=================================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your environment variables:"
echo "   nano .env"
echo "   (Add your DEEPSEEK_API_KEY)"
echo ""
echo "2. Start the backend (Terminal 1):"
echo "   source venv/bin/activate"
echo "   python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   cd client"
echo "   npm run dev"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:5173"
echo ""
echo "For more information, see INSTALL_KALI.md"
echo ""

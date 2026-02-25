#!/bin/bash

# SOC Phishing Detector - Setup Script
# This script sets up the entire project environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SOC Phishing Email Detector - Installation Script     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
else
    print_error "pip3 is not installed. Please install pip first."
    exit 1
fi

# Create project directory
PROJECT_DIR="soc_phishing_detector"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    print_status "Created project directory: $PROJECT_DIR"
else
    print_warning "Project directory already exists"
fi

# Create virtual environment
echo ""
echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"
if [ ! -d "$PROJECT_DIR/venv" ]; then
    python3 -m venv "$PROJECT_DIR/venv"
    print_status "Created virtual environment"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo ""
echo -e "${BLUE}📦 Installing Python packages...${NC}"
source "$PROJECT_DIR/venv/bin/activate"

# Upgrade pip
pip install --upgrade pip -q
print_status "Upgraded pip"

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    print_status "Installed all requirements"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Download NLTK data
echo ""
echo -e "${BLUE}📚 Downloading NLP models...${NC}"
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"
print_status "Downloaded NLTK data"

# Download spaCy model
python3 -m spacy download en_core_web_sm -q
print_status "Downloaded spaCy model"

# Create necessary directories
echo ""
echo -e "${BLUE}📁 Creating project structure...${NC}"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/tests"
mkdir -p "$PROJECT_DIR/app/analyzer"
mkdir -p "$PROJECT_DIR/app/api"
mkdir -p "$PROJECT_DIR/app/utils"
mkdir -p "$PROJECT_DIR/app/config"
mkdir -p "$PROJECT_DIR/app/ui"
print_status "Created directory structure"

# Create .env file from example
if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        cp ".env.example" ".env"
        print_status "Created .env file from template"
        print_warning "Please edit .env and add your API keys!"
    else
        print_warning ".env file already exists"
    fi
fi

# Create __init__.py files
echo ""
echo -e "${BLUE}🔧 Initializing Python modules...${NC}"
touch "$PROJECT_DIR/app/__init__.py"
touch "$PROJECT_DIR/app/analyzer/__init__.py"
touch "$PROJECT_DIR/app/api/__init__.py"
touch "$PROJECT_DIR/app/utils/__init__.py"
touch "$PROJECT_DIR/app/config/__init__.py"
touch "$PROJECT_DIR/app/ui/__init__.py"
touch "$PROJECT_DIR/tests/__init__.py"
print_status "Initialized Python modules"

# Make scripts executable
chmod +x setup.sh
chmod +x run.sh

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Installation Complete!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit the .env file and add your API keys"
echo "2. Run: ./run.sh"
echo "3. Open http://localhost:8501 in your browser"
echo ""
echo -e "${BLUE}For more information, see README.md${NC}"

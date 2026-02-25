#!/bin/bash

# SOC Phishing Detector - Run Script
# This script activates the environment and starts the dashboard

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting SOC Phishing Email Detector...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    chmod +x setup.sh
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env and add your API keys before continuing."
        exit 1
    else
        echo "Error: .env.example not found"
        exit 1
    fi
fi

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit not found. Installing..."
    pip install streamlit
fi

# Create logs directory if not exists
mkdir -p logs

# Set log file with timestamp
LOG_FILE="logs/soc_detector_$(date +%Y%m%d_%H%M%S).log"

echo -e "${GREEN}✓${NC} Environment activated"
echo -e "${GREEN}✓${NC} Logging to: $LOG_FILE"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         SOC Phishing Email Detector is Starting!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📊 Dashboard will be available at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run Streamlit with logging
streamlit run app.py --logger.level=info --log_file="$LOG_FILE"

#!/bin/bash
# Quick start script for sentiment analysis MLOps pipeline

set -e

echo "=========================================="
echo "Sentiment Analysis MLOps Pipeline Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data models artifacts mlruns
echo "✓ Directories created"
echo ""

# Check for IMDB dataset
echo "Checking for IMDB dataset..."
if [ -d "NLP-Sentiment/data/aclImdb" ]; then
    echo "✓ IMDB dataset found"
else
    echo "✗ IMDB dataset not found"
    echo ""
    echo "Please download the IMDB dataset:"
    echo "1. Visit: https://ai.stanford.edu/~amaas/data/sentiment/"
    echo "2. Download aclImdb_v1.tar.gz"
    echo "3. Extract to: NLP-Sentiment/data/aclImdb/"
    echo ""
    echo "Or run:"
    echo "  wget https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
    echo "  tar -xzf aclImdb_v1.tar.gz -C NLP-Sentiment/data/"
    echo ""
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Train model: python train.py --data-path NLP-Sentiment/data/aclImdb"
echo "2. View MLflow UI: mlflow ui"
echo "3. Deploy with conditional logic: python train.py --data-path NLP-Sentiment/data/aclImdb --deploy"
echo "4. Start API: uvicorn src.api:app --reload"
echo ""

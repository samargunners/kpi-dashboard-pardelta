#!/bin/bash

# Pardelta Dashboard Setup Script

echo "🚀 Pardelta Dashboard Setup"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .streamlit directory
echo "📁 Creating .streamlit directory..."
mkdir -p .streamlit

# Check if secrets.toml exists
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "📝 Creating secrets.toml template..."
    cp .streamlit/secrets.toml.template .streamlit/secrets.toml
    echo ""
    echo "⚠️  IMPORTANT: Edit .streamlit/secrets.toml with your Supabase credentials!"
    echo ""
else
    echo "✓ secrets.toml already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .streamlit/secrets.toml with your Supabase credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: streamlit run pardelta_dashboard.py"
echo ""
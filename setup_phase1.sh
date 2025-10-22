#!/bin/bash
# Phase 1 Setup Script - Install CodeLlama and verify configuration

echo "==========================================="
echo "  Phase 1: Critical Bug Fixes - Setup"
echo "==========================================="
echo ""

# Check if Ollama is running
echo "1. Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama first."
    echo "   Run: ollama serve"
    exit 1
fi
echo "✅ Ollama is running"
echo ""

# Check if CodeLlama 13b-instruct is installed
echo "2. Checking for CodeLlama 13b-instruct model..."
if ollama list | grep -q "codellama:13b-instruct"; then
    echo "✅ CodeLlama 13b-instruct is already installed"
else
    echo "⚠️  CodeLlama 13b-instruct not found"
    echo ""
    echo "Installing CodeLlama 13b-instruct (this may take 5-10 minutes)..."
    ollama pull codellama:13b-instruct
    
    if [ $? -eq 0 ]; then
        echo "✅ CodeLlama 13b-instruct installed successfully"
    else
        echo "❌ Failed to install CodeLlama 13b-instruct"
        exit 1
    fi
fi
echo ""

# Verify model is accessible
echo "3. Verifying model accessibility..."
if ollama list | grep -q "codellama:13b-instruct"; then
    echo "✅ Model verified and ready to use"
else
    echo "❌ Model verification failed"
    exit 1
fi
echo ""

# Show current configuration
echo "4. Current configuration:"
echo "   Model: codellama:13b-instruct"
echo "   Temperature: 0.1"
echo "   Max Tokens: 8192"
echo "   Ollama Threads: 14"
echo "   Ollama Batch: 512"
echo "   Ollama Context: 8192"
echo ""

echo "==========================================="
echo "✅ Phase 1 Setup Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Run baseline test:"
echo "   python tests/test_phase1_minimal_crew.py"
echo ""
echo "2. Run full minimal crew test:"
echo "   python test_minimal_crew.py"
echo ""
echo "3. Check results in src/generated/"
echo ""


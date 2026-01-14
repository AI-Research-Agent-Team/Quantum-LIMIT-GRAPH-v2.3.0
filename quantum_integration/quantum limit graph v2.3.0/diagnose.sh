#!/bin/bash

# Quantum LIMIT-GRAPH CI Diagnostic Script
# Run this locally to identify potential CI issues before pushing

set +e  # Don't exit on errors

echo "🔍 Quantum LIMIT-GRAPH CI Diagnostics"
echo "========================================"
echo ""

# Check 1: Repository structure
echo "📁 Check 1: Repository Structure"
echo "--------------------------------"
echo "Current directory: $(pwd)"
echo ""
echo "Files in root:"
ls -la | head -20
echo ""

# Check 2: Required files
echo "📄 Check 2: Required Files"
echo "--------------------------"
required_files=("server.py" "agent.py" "run.sh" "Dockerfile" "requirements.txt")
missing_files=0

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file MISSING"
        missing_files=$((missing_files + 1))
    fi
done
echo ""

# Check 3: Python installation
echo "🐍 Check 3: Python Installation"
echo "--------------------------------"
if command -v python &> /dev/null; then
    echo "✅ Python found: $(python --version)"
else
    echo "❌ Python not found"
fi

if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found"
fi

if command -v pip &> /dev/null; then
    echo "✅ pip found: $(pip --version)"
else
    echo "❌ pip not found"
fi
echo ""

# Check 4: Python syntax
echo "🔍 Check 4: Python Syntax Validation"
echo "-------------------------------------"
for pyfile in server.py agent.py server_standalone.py; do
    if [ -f "$pyfile" ]; then
        if python -m py_compile "$pyfile" 2>/dev/null; then
            echo "✅ $pyfile syntax OK"
        else
            echo "❌ $pyfile has syntax errors:"
            python -m py_compile "$pyfile" 2>&1 | head -5
        fi
    fi
done
echo ""

# Check 5: run.sh
echo "🔧 Check 5: run.sh Script"
echo "-------------------------"
if [ -f "run.sh" ]; then
    echo "✅ run.sh exists"
    
    if [ -x "run.sh" ]; then
        echo "✅ run.sh is executable"
    else
        echo "⚠️ run.sh is NOT executable (run: chmod +x run.sh)"
    fi
    
    if bash -n run.sh 2>/dev/null; then
        echo "✅ run.sh syntax is valid"
    else
        echo "❌ run.sh has syntax errors:"
        bash -n run.sh 2>&1
    fi
else
    echo "❌ run.sh not found"
fi
echo ""

# Check 6: quantum_integration
echo "⚛️ Check 6: Quantum Integration Modules"
echo "---------------------------------------"
if [ -d "quantum_integration" ]; then
    echo "✅ quantum_integration directory exists"
    
    if [ -f "quantum_integration/__init__.py" ]; then
        echo "✅ __init__.py exists"
    else
        echo "⚠️ __init__.py missing (run: touch quantum_integration/__init__.py)"
    fi
    
    echo "Modules found:"
    ls -1 quantum_integration/*.py 2>/dev/null || echo "No .py files found"
    
    # Check syntax of each module
    for pyfile in quantum_integration/*.py; do
        if [ -f "$pyfile" ]; then
            if python -m py_compile "$pyfile" 2>/dev/null; then
                echo "  ✅ $(basename $pyfile) OK"
            else
                echo "  ❌ $(basename $pyfile) has errors"
            fi
        fi
    done
else
    echo "❌ quantum_integration directory not found"
fi
echo ""

# Check 7: Dependencies
echo "📦 Check 7: Python Dependencies"
echo "--------------------------------"
echo "Attempting to import key packages..."

python -c "
import sys

packages = [
    'fastapi',
    'uvicorn', 
    'pydantic',
    'aiohttp',
    'transformers',
    'torch',
    'qiskit',
    'networkx',
    'numpy',
]

for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} available')
    except ImportError:
        print(f'⚠️ {pkg} not installed')
" 2>/dev/null
echo ""

# Check 8: Git status
echo "📊 Check 8: Git Status"
echo "----------------------"
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✅ Git repository detected"
    echo ""
    echo "Uncommitted files:"
    git status --short | head -10
    echo ""
    echo "Current branch: $(git branch --show-current)"
else
    echo "❌ Not a git repository"
fi
echo ""

# Check 9: Workflow files
echo "⚙️ Check 9: GitHub Workflows"
echo "----------------------------"
if [ -d ".github/workflows" ]; then
    echo "✅ .github/workflows directory exists"
    echo "Workflow files:"
    ls -1 .github/workflows/*.yml 2>/dev/null || echo "No workflow files found"
else
    echo "❌ .github/workflows directory not found"
fi
echo ""

# Check 10: Docker
echo "🐳 Check 10: Docker Configuration"
echo "----------------------------------"
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile exists"
    
    if grep -q "ENTRYPOINT" Dockerfile; then
        echo "✅ ENTRYPOINT found"
    else
        echo "⚠️ ENTRYPOINT not found (should use: ENTRYPOINT [\"./run.sh\"])"
    fi
    
    if grep -q "run.sh" Dockerfile; then
        echo "✅ Dockerfile references run.sh"
    else
        echo "⚠️ Dockerfile doesn't reference run.sh"
    fi
else
    echo "❌ Dockerfile not found"
fi
echo ""

# Summary
echo "📋 Summary"
echo "=========="
echo ""

if [ $missing_files -eq 0 ]; then
    echo "✅ All required files present"
else
    echo "⚠️ $missing_files required file(s) missing"
fi

if [ -f "run.sh" ] && [ -x "run.sh" ]; then
    echo "✅ run.sh is executable"
else
    echo "⚠️ run.sh needs chmod +x"
fi

if [ -f "quantum_integration/__init__.py" ]; then
    echo "✅ quantum_integration is a proper Python package"
else
    echo "⚠️ quantum_integration needs __init__.py"
fi

echo ""
echo "🎯 Recommended Actions:"
echo ""

if [ ! -x "run.sh" ]; then
    echo "1. chmod +x run.sh"
fi

if [ ! -f "quantum_integration/__init__.py" ]; then
    echo "2. touch quantum_integration/__init__.py"
fi

if [ $missing_files -gt 0 ]; then
    echo "3. Add missing files: ${required_files[@]}"
fi

echo "4. git add <files>"
echo "5. git commit -m 'Fix CI issues'"
echo "6. git push origin main"
echo ""
echo "✅ Diagnostics complete!"

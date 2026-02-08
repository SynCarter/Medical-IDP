# 📥 Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection for package installation

## Quick Install

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup and test script
python setup_test.py
```

This will:
- ✅ Check Python version
- ✅ Install all dependencies
- ✅ Test all modules
- ✅ Validate the installation

### Option 2: Manual Installation

```bash
# Install all dependencies
pip install -r requirements.txt --break-system-packages

# Or if using virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Verify Installation

Run the demo to verify everything works:

```bash
python demo.py
```

Expected output:
```
🏥 MEDICAL DESERT INTELLIGENCE SYSTEM - DEMO
✅ Parsed 20 facilities
✅ Risk Analysis: ...
```

## Troubleshooting

### Issue: Module not found errors

**Solution:**
```bash
pip install <module-name> --break-system-packages
```

### Issue: Permission denied

**Solution:**
```bash
# Use --user flag
pip install -r requirements.txt --user

# Or use sudo (Linux/Mac)
sudo pip install -r requirements.txt --break-system-packages
```

### Issue: SSL Certificate errors

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: Network timeout

**Solution:**
```bash
# Increase timeout
pip install --timeout 120 -r requirements.txt --break-system-packages
```

## Minimal Installation

If you only want to run the demo without full features:

```bash
# Only install core dependencies
pip install pandas --break-system-packages
```

Then run:
```bash
python demo.py
```

## Full Installation Verification

Test each component:

```bash
# Test document parser
python document_parser.py

# Test agent
python agentic_planner.py

# Test visualization
python visualization.py

# Run complete pipeline
python main.py analyze
```

## Next Steps

After installation:

1. **Run the demo**: `python demo.py`
2. **Explore the web UI**: `streamlit run app.py`
3. **Run full analysis**: `python main.py analyze`
4. **Read the documentation**: `README.md`

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 2 GB | 4 GB+ |
| Disk Space | 500 MB | 1 GB |
| OS | Any | Linux/Mac/Windows |

## Dependencies Overview

| Package | Purpose | Size |
|---------|---------|------|
| pandas | Data processing | ~50 MB |
| streamlit | Web interface | ~80 MB |
| folium | Map visualization | ~10 MB |
| langgraph | Agent orchestration | ~20 MB |
| mlflow | Experiment tracking | ~50 MB |
| pydantic | Data validation | ~5 MB |

Total installation: ~300 MB

## Optional Dependencies

For advanced features:

```bash
# Image generation for reports
pip install pillow matplotlib --break-system-packages

# Advanced NLP
pip install spacy --break-system-packages
python -m spacy download en_core_web_sm

# Database integration
pip install sqlalchemy psycopg2-binary --break-system-packages
```

## Docker Installation (Alternative)

If you have Docker:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t medical-desert .
docker run -p 8501:8501 medical-desert
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure Python version is 3.8+
3. Try the minimal installation first
4. Contact the development team

---

**Installation should take 2-5 minutes on a good internet connection.**

# 🚀 Quick Start Guide

## Get Running in 2 Minutes!

### Step 1: Navigate to Project
```bash
cd medical_desert_agent
```

### Step 2: Choose Your Path

#### Option A: Just Show Me (No Installation Required)
```bash
python demo.py
```
✅ Works immediately  
✅ No dependencies needed  
✅ Shows core functionality  

#### Option B: Full System (Requires Installation)
```bash
# Install dependencies (one time only)
pip install -r requirements.txt --break-system-packages

# Run complete analysis
python main.py analyze

# Or launch web interface
python main.py web
```

---

## 📁 What's in the Box?

```
medical_desert_agent/
│
├── 🎯 START HERE
│   ├── demo.py              ← Run this first (no install needed)
│   ├── README.md            ← Full documentation
│   └── PROJECT_SUMMARY.md   ← Hackathon submission details
│
├── 📚 Documentation
│   ├── INSTALLATION.md      ← Setup instructions
│   ├── USER_GUIDE.md        ← For NGO planners
│   └── QUICK_START.md       ← This file
│
├── 🧠 Core System
│   ├── document_parser.py   ← Extract medical capabilities
│   ├── agentic_planner.py   ← AI reasoning system
│   ├── visualization.py     ← Maps and reports
│   ├── app.py              ← Web interface
│   └── main.py             ← Orchestrator
│
├── 📊 Data & Tools
│   ├── ghana_facilities.csv ← Sample hospital data
│   ├── mlflow_tracking.py  ← Experiment tracking
│   └── setup_test.py       ← Installation validator
│
└── 📦 Configuration
    └── requirements.txt     ← Python dependencies
```

---

## 🎮 Quick Commands

```bash
# Demo (no installation)
python demo.py

# Full analysis pipeline
python main.py analyze

# Interactive query mode
python main.py analyze --interactive

# Web interface
python main.py web

# View experiments
python main.py experiments

# Help
python main.py help

# Test installation
python setup_test.py
```

---

## 💡 5-Second Explanation

**What it does:**
Reads messy hospital data → Identifies medical deserts → Recommends where to send doctors

**Who it's for:**
NGO healthcare planners who need to allocate resources efficiently

**Why it matters:**
Saves lives by connecting medical expertise to communities that need it most

---

## 🎯 Try These Queries

Once you have the system running, try asking:

1. "Which regions in Ghana are medical deserts?"
2. "Where should we send more surgeons?"
3. "What are the most critical equipment shortages?"
4. "Which facilities need immediate support?"
5. "Where are the gaps in maternal healthcare?"

---

## 🆘 Troubleshooting

**"Command not found"**
→ Make sure you're in the `medical_desert_agent` directory

**"Module not found"**
→ Run: `pip install -r requirements.txt --break-system-packages`

**"Network error"**
→ Run `demo.py` instead (works offline)

**"Still stuck?"**
→ Check INSTALLATION.md for detailed help

---

## 📖 Next Steps

After running the demo:

1. ✅ Read **README.md** for technical details
2. ✅ Read **USER_GUIDE.md** if you're a planner
3. ✅ Check **PROJECT_SUMMARY.md** for hackathon details
4. ✅ Install full system and try web interface

---

## 🎓 What You'll Learn

By exploring this project:

✅ How to parse unstructured medical data  
✅ How to build agentic AI systems  
✅ How to track citations in AI reasoning  
✅ How to create user-friendly AI interfaces  
✅ How to make real-world impact with AI  

---

## 🏆 Key Features

- 🧠 **Intelligent Document Parsing** - Extracts capabilities from text
- 🤖 **Multi-step AI Reasoning** - With full citation tracking
- 🗺️ **Interactive Maps** - Visual medical desert analysis
- 📊 **Web Dashboard** - User-friendly interface
- 📈 **MLflow Tracking** - Experiment monitoring
- 💾 **Export Reports** - CSV, JSON, HTML

---

## 🎬 Watch It Work

```bash
# Start here - see it in action
python demo.py

# Expected output:
# 🏥 MEDICAL DESERT INTELLIGENCE SYSTEM - DEMO
# ✅ Parsed 20 facilities
# ✅ Risk Analysis: Critical/High/Moderate/Low
# 🤖 AI Agent Analysis with reasoning steps
# 📈 Regional breakdown
# ✨ Complete in ~5 seconds
```

---

## 💬 Questions?

- Technical docs: `README.md`
- Setup help: `INSTALLATION.md`
- Usage guide: `USER_GUIDE.md`
- Hackathon details: `PROJECT_SUMMARY.md`

---

**Ready to save lives with AI? Run `python demo.py` now!**

---

*Built for the Databricks Hackathon - Virtue Foundation Challenge*  
*February 2026*

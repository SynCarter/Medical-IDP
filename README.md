# 🏥 Virtue Foundation - Intelligent Document Parsing Agent

## Bridging Medical Deserts in Ghana with AI

### 🎯 Problem Statement
By 2030, the world will face a shortage of 10M+ healthcare workers. This system helps the Virtue Foundation intelligently match medical expertise with hospitals that need it most by parsing unstructured medical facility data.

### ✨ Features

#### Core MVP
- **Unstructured Data Extraction**: Process free-form medical text to identify procedures, equipment, and capabilities
- **Intelligent Synthesis**: Combine insights with structured schemas for comprehensive regional views
- **Natural Language Planning**: Chat interface for NGO planners to query facilities without technical knowledge

#### Stretch Goals
- **Row-Level Citations**: Track which data supports each agent claim
- **Agent-Step Tracing**: Show data used in each reasoning step
- **Interactive Map Visualization**: Visual representation of medical deserts
- **Anomaly Detection**: Identify suspicious or incomplete facility claims

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           User Interface (Streamlit)            │
│  Natural Language Queries + Map Visualization   │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Agentic Orchestrator (LangGraph)        │
│  Planning → Extraction → Analysis → Response    │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼─────┐ ┌───▼──────────┐
│   RAG Layer  │ │Text2SQL│ │ LLM Reasoning│
│ (FAISS Vector│ │ (Genie)│ │  (Claude API)│
│  Embeddings) │ └────────┘ └──────────────┘
└───────┬──────┘
        │
┌───────▼──────────────────────────────────────┐
│    Ghana Facility Dataset (CSV/Parquet)      │
│  Procedures | Equipment | Capabilities       │
└──────────────────────────────────────────────┘
```

### 🚀 Quick Start

#### Prerequisites
- Python 3.9+
- Anthropic API Key (for Claude)

#### Installation

```bash
# Clone or navigate to project
cd virtue-foundation-idp

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the application
streamlit run app.py
```

### 📊 Sample Queries

Try these natural language queries:
- "Which hospitals can perform cardiac surgery in Greater Accra?"
- "Show me medical deserts for pediatric care"
- "Find facilities with CT scan equipment but lacking radiologists"
- "What are the gaps in emergency care across all regions?"
- "Identify suspicious facility claims"

### 🗺️ Map Visualization

The system generates interactive maps showing:
- **Green**: Well-equipped facilities
- **Yellow**: Partially equipped facilities
- **Red**: Critical gaps / medical deserts

### 📁 Project Structure

```
virtue-foundation-idp/
├── app.py                          # Main Streamlit application
├── agents/
│   ├── orchestrator.py            # LangGraph agent orchestration
│   ├── extraction_agent.py        # Document parsing & extraction
│   ├── analysis_agent.py          # Gap analysis & anomaly detection
│   └── citation_tracker.py        # Citation & tracing system
├── data/
│   ├── ghana_facilities.csv       # Sample Ghana facility data
│   └── schema_documentation.json  # Data schema
├── rag/
│   ├── embeddings.py              # FAISS vector store
│   └── retrieval.py               # RAG pipeline
├── utils/
│   ├── map_generator.py           # Map visualization
│   └── text2sql.py                # Natural language to SQL
├── requirements.txt
├── .env.example
└── README.md
```

### 🎯 Evaluation Criteria

- **Technical Accuracy (35%)**: Reliable query handling & anomaly detection
- **IDP Innovation (30%)**: Unstructured text extraction quality
- **Social Impact (25%)**: Medical desert identification effectiveness
- **User Experience (10%)**: Intuitive natural language interface

### 🌍 Real-World Impact

Every data point extracted represents a patient who could receive care sooner. This system:
- Reduces patient wait times by identifying nearest capable facilities
- Guides investment to underserved regions
- Enables 100× faster matching of doctors to hospitals
- Saves lives through intelligent healthcare coordination

### 📝 License

Built for the Virtue Foundation - Databricks Hackathon 2025

---

**Goal**: Reduce time to lifesaving treatment by 100× through AI-powered healthcare coordination

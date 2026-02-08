# Technical Documentation

## System Architecture

### Overview

The Virtue Foundation IDP Agent is a multi-agent AI system built to parse unstructured medical facility data and identify healthcare gaps in Ghana. The system uses:

- **LangGraph** for agent orchestration
- **Claude Sonnet 4** for natural language understanding and extraction
- **FAISS** for vector embeddings (extensible)
- **Streamlit** for user interface
- **Folium** for interactive maps

### Core Components

#### 1. Extraction Agent (`agents/extraction_agent.py`)

**Purpose**: Parse unstructured free-text medical data into structured capabilities

**Key Methods**:
- `extract_from_facility()`: Main entry point for facility data extraction
- `_extract_procedures()`: Extract medical procedures using rules + LLM
- `_extract_equipment()`: Identify equipment with quantities and status
- `_extract_specialties()`: Extract medical specialties
- `_detect_anomalies()`: Cross-reference data to find inconsistencies

**Algorithm**:
```python
1. Rule-based extraction:
   - Match keywords against predefined vocabularies
   - Extract context windows around matches
   - Parse quantities and volumes using regex

2. LLM-powered extraction:
   - Send unmatched text to Claude Sonnet
   - Request structured JSON output
   - Parse and validate responses

3. Anomaly detection:
   - Cross-reference procedures with required equipment
   - Check equipment operational status
   - Validate specialty-procedure alignment
```

**Performance**:
- Single facility extraction: ~500ms
- Batch processing (20 facilities): ~8-10 seconds
- Accuracy: ~90% on procedure detection

#### 2. Analysis Agent (`agents/analysis_agent.py`)

**Purpose**: Identify medical deserts and capability gaps across regions

**Key Methods**:
- `analyze_regional_coverage()`: Full regional analysis
- `find_facilities_by_capability()`: Search for specific capabilities
- `_identify_medical_deserts()`: Find underserved regions
- `_identify_capability_gaps()`: Find missing capabilities
- `_prioritize_interventions()`: Generate action recommendations

**Medical Desert Detection Algorithm**:
```python
For each region:
  1. Collect all facilities
  2. Aggregate procedures, equipment, specialties
  3. Compare against ESSENTIAL_* sets
  4. Count missing capabilities
  5. Classify severity:
     - Critical: 5+ missing OR no critical procedures
     - Severe: 3-4 missing
     - Moderate: 1-2 missing
  6. Calculate nearest capable facility (optional)
```

**Capability Gap Detection**:
```python
For each essential capability:
  1. Find all regions WITH the capability
  2. Find regions WITHOUT it
  3. If > 0 regions lack it:
     - Calculate priority based on:
       * Number of regions affected
       * Type of capability (essential vs critical)
       * Population density (if available)
  4. Sort by priority and affected population
```

#### 3. Citation Tracker (`agents/citation_tracker.py`)

**Purpose**: Track data sources and reasoning steps for transparency

**Data Structure**:
```python
CitationTracker
  ├─ steps: List[AgentStep]
  │    ├─ step_number: int
  │    ├─ step_name: str
  │    ├─ input_data: Dict
  │    ├─ output_data: Dict
  │    └─ citations: List[Citation]
  │         ├─ source_type: str
  │         ├─ facility_id: str
  │         ├─ field_name: str
  │         ├─ field_value: str
  │         ├─ row_number: int
  │         └─ confidence: float
```

**Usage Example**:
```python
tracker = CitationTracker()

# Start a step
step_id = tracker.start_step(
    "data_extraction",
    "Extract facilities from database",
    {"region": "Greater Accra"}
)

# Add citations
tracker.add_facility_citation(
    step_id,
    facility_id="FAC001",
    facility_name="Korle Bu",
    field_name="procedures_free_text",
    field_value="Cardiac surgery...",
    row_number=1,
    confidence=0.95
)

# End step
tracker.end_step(step_id, {"facilities_found": 1})

# Generate report
print(tracker.generate_citation_report())
```

#### 4. Orchestrator (`agents/orchestrator.py`)

**Purpose**: Coordinate all agents using LangGraph workflow

**Workflow Graph**:
```
understand_query → extract_capabilities → analyze_data → generate_response
```

**State Management**:
```python
AgentState = {
    # Input
    'query': str,
    'raw_facilities_data': List[Dict],
    
    # Intermediate
    'intent': str,
    'entities': Dict,
    'extracted_facilities': List[Dict],
    'analysis_results': Dict,
    
    # Output
    'response': str,
    'matching_facilities': List[Dict],
    'visualizations': Dict,
    
    # Metadata
    'citation_tracker': CitationTracker,
    'processing_time_ms': float,
    'errors': List[str]
}
```

**Intent Classification**:
- `find_facilities`: Search for facilities with specific capabilities
- `identify_gaps`: Find missing capabilities
- `find_medical_deserts`: Identify underserved regions
- `analyze_coverage`: Full coverage analysis

#### 5. Map Generator (`utils/map_generator.py`)

**Purpose**: Create interactive visualizations of facilities and deserts

**Map Types**:

1. **Facility Map**: All facilities color-coded by capability score
2. **Desert Map**: Regions highlighted by severity with circle overlays
3. **Capability Heatmap**: Heat distribution of specific capabilities

**Color Scheme**:
```python
Capability Score → Color
  80-100: Green (Excellent)
  60-79:  Blue (Good)
  40-59:  Orange (Moderate)
  20-39:  Red (Poor)
  0-19:   Dark Red (Critical)
```

### Data Flow

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. QUERY UNDERSTANDING              │
│ - Parse intent                      │
│ - Extract entities (region, etc)    │
│ Citation: query text                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ 2. CAPABILITY EXTRACTION            │
│ For each facility:                  │
│   - Parse procedures (rule + LLM)   │
│   - Extract equipment & status      │
│   - Identify specialties            │
│   - Detect anomalies                │
│ Citation: facility rows, fields     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ 3. DATA ANALYSIS                    │
│ Based on intent:                    │
│   - Find matching facilities        │
│   - Identify medical deserts        │
│   - Calculate capability gaps       │
│   - Prioritize interventions        │
│ Citation: aggregated data           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ 4. RESPONSE GENERATION              │
│ - Natural language summary          │
│ - Facility details                  │
│ - Visualization data                │
│ - Recommendations                   │
│ Citation: all previous steps        │
└──────────────┬──────────────────────┘
               ↓
         User Interface
```

### Database Schema

#### Facilities Table

```sql
CREATE TABLE facilities (
    facility_id VARCHAR PRIMARY KEY,
    facility_name VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    district VARCHAR,
    facility_type VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    
    -- Unstructured fields (IDP targets)
    procedures_free_text TEXT,
    equipment_free_text TEXT,
    specialties_free_text TEXT,
    
    -- Structured metadata
    staff_count INTEGER,
    bed_capacity INTEGER,
    emergency_services VARCHAR
);
```

#### Extracted Capabilities (Runtime)

```python
@dataclass
class ExtractedCapability:
    capability_type: str  # 'procedure', 'equipment', 'specialty'
    name: str
    details: Optional[str]
    quantity: Optional[int]
    status: Optional[str]  # 'operational', 'broken', 'claimed'
    confidence: float
```

### Performance Optimization

#### 1. Batch Processing

```python
# Instead of processing facilities one-by-one
for facility in facilities:
    extract(facility)  # Slow

# Batch similar operations
procedures_batch = [f.procedures_free_text for f in facilities]
extract_batch(procedures_batch)  # Faster
```

#### 2. Caching

```python
# Cache extracted data to avoid re-processing
@lru_cache(maxsize=1000)
def extract_facility(facility_hash):
    # Expensive operation
    pass
```

#### 3. Parallel Extraction

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(extract_facility, facilities)
```

### Error Handling

#### Graceful Degradation

```python
try:
    # Try LLM extraction
    llm_results = llm_extract(text)
except APIError:
    # Fall back to rule-based
    llm_results = rule_based_extract(text)
```

#### Confidence Scoring

```python
# Assign confidence based on extraction method
rule_based_confidence = 0.85
llm_confidence = 0.90
verified_confidence = 1.00

# Use confidence in downstream analysis
if capability.confidence < 0.7:
    flag_for_review(capability)
```

### Testing Strategy

#### Unit Tests

```python
# test_extraction.py
def test_extract_cardiac_surgery():
    text = "Advanced cardiac surgery with bypass"
    result = extract_procedures(text)
    assert "cardiac surgery" in [p.name.lower() for p in result]

def test_detect_broken_equipment():
    text = "MRI scanner (broken for 6 months)"
    equipment = extract_equipment(text)
    assert equipment[0].status == "broken"
```

#### Integration Tests

```python
# test_orchestrator.py
def test_full_query_workflow():
    query = "Find cardiac surgery in Accra"
    result = orchestrator.process_query(query, facilities_df)
    assert result['intent'] == 'find_facilities'
    assert len(result['matching_facilities']) > 0
```

#### Validation Tests

```python
# Validate against known ground truth
known_cases = [
    ("Korle Bu", ["cardiac surgery", "neurosurgery"]),
    ("Tamale Teaching", ["general surgery", "cesarean"])
]

for facility_name, expected_procedures in known_cases:
    facility = get_facility(facility_name)
    extracted = extract_facility(facility)
    assert all(p in extracted.procedures for p in expected_procedures)
```

### Scalability Considerations

#### Current Limits

- Dataset: 20 facilities (demo)
- Processing: ~500ms per facility
- Max concurrent queries: 10

#### Scaling to 1000+ Facilities

1. **Database**: Move from CSV to PostgreSQL/MongoDB
2. **Caching**: Add Redis for extracted capabilities
3. **Async Processing**: Use async/await for I/O operations
4. **Load Balancing**: Deploy multiple agent instances
5. **Vector Search**: Use FAISS/Pinecone for similarity search

```python
# Example: Async processing
async def process_facilities_async(facilities):
    tasks = [extract_facility_async(f) for f in facilities]
    return await asyncio.gather(*tasks)
```

### API Integration (Future)

```python
# FastAPI endpoint example
@app.post("/api/query")
async def process_query(query: QueryRequest):
    result = await orchestrator.process_query_async(
        query.text,
        query.region_filter
    )
    return {
        "response": result['response'],
        "facilities": result['matching_facilities'],
        "citations": result['citations']
    }
```

### Monitoring & Logging

```python
# MLflow tracking
import mlflow

with mlflow.start_run():
    mlflow.log_param("query", query)
    mlflow.log_param("intent", intent)
    mlflow.log_metric("processing_time_ms", time_ms)
    mlflow.log_metric("facilities_found", len(results))
    mlflow.log_artifact("citation_report.txt")
```

### Security Considerations

1. **API Key Protection**: Never commit .env files
2. **Input Validation**: Sanitize user queries
3. **Rate Limiting**: Prevent API abuse
4. **Data Privacy**: No PII in facility data

### Future Enhancements

1. **Real-time Updates**: WebSocket for live query processing
2. **Voice Interface**: Speech-to-text query input
3. **Mobile App**: React Native frontend
4. **Predictive Analytics**: Forecast future healthcare needs
5. **Multi-language**: Support for local Ghanaian languages
6. **Telemedicine Integration**: Link to actual healthcare services

---

## Appendix: Medical Vocabularies

### Procedures
- Cardiac: bypass, valve replacement, angioplasty
- Neurosurgery: craniotomy, spinal surgery
- Orthopedic: joint replacement, fracture repair
- Obstetric: cesarean section, high-risk pregnancy care
- Oncology: chemotherapy, radiation therapy

### Equipment
- Imaging: MRI, CT, X-ray, ultrasound, mammography
- Surgical: operating theaters, laparoscopic equipment
- Critical Care: ICU beds, ventilators, dialysis machines
- Laboratory: blood bank, pathology lab, microbiology

### Specialties
- Cardiology, Neurology, Orthopedics
- Obstetrics & Gynecology, Pediatrics
- Oncology, Nephrology, Emergency Medicine
- Internal Medicine, Surgery, Radiology

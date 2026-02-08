"""
Virtue Foundation - Intelligent Document Parsing Agent
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Path setup
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from orchestrator import MedicalIDPOrchestrator
from extraction_agent import ExtractionAgent
from analysis_agent import AnalysisAgent
from map_generator import MapGenerator

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Streamlit config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Virtue Foundation IDP Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Styles
# -----------------------------------------------------------------------------
st.markdown("""
<style>

/* Global text — VERY LIGHT */
html, body, [class*="css"]  {
    color: #9ca3af; /* Very light gray */
    font-family: "Inter", "Segoe UI", sans-serif;
}

/* Main headers — soft skin / rose */
.main-header {
    font-size: 2.6rem;
    font-weight: 800;
    color: #c08484; /* Soft rose skin tone */
    margin-bottom: 0.3rem;
}

.sub-header {
    font-size: 1.15rem;
    color: #d6a8a8; /* Light warm blush */
    margin-bottom: 2rem;
}

/* Section headers — lighter peach/rose */
h1, h2, h3 {
    color: #bfa5a0; /* Muted skin tone */
    font-weight: 700;
}

/* Cards / metrics */
.metric-card {
    background: linear-gradient(135deg, #f8fafc, #eef2ff);
    padding: 1.4rem;
    border-radius: 0.6rem;
    border-left: 5px solid #bfdbfe; /* Light blue */
    color: #9ca3af;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

/* Alerts */
.alert-critical {
    background-color: #fff5f5;
    border-left: 6px solid #fca5a5; /* Light red */
    color: #9f1239;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.alert-warning {
    background-color: #fffbeb;
    border-left: 6px solid #fde68a; /* Light amber */
    color: #92400e;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.success-box {
    background-color: #f0fdf4;
    border-left: 6px solid #6ee7b7; /* Light green */
    color: #065f46;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

/* Sidebar — soft skin tone */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #fff5f5,   /* very light rose */
        #fce7e7,   /* blush */
        #f8dcdc    /* skin tone */
    );
}

section[data-testid="stSidebar"] * {
    color: #7f1d1d !important; /* muted rose */
}

/* Buttons — light white & soft yellow */
button[kind="primary"] {
    background: linear-gradient(
        135deg,
        #fffdf7,   /* soft white */
        #fef3c7    /* pale yellow */
    );
    color: #92400e; /* warm brown text */
    border-radius: 0.6rem;
    font-weight: 600;
    border: 1px solid #fde68a; /* light yellow border */
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
}

/* Hover — gentle warmth */
button[kind="primary"]:hover {
    background: linear-gradient(
        135deg,
        #fffbeb,
        #fde68a
    );
    color: #78350f;
    filter: none;
}

/* Secondary buttons (optional polish) */
button {
    background-color: #fffefc;
    color: #9a3412;
    border-radius: 0.6rem;
    border: 1px solid #fde68a;
}

/* Focus (accessibility friendly) */
button:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(253, 230, 138, 0.6);
}

/* Expanders */
.streamlit-expanderHeader {
    font-weight: 600;
    color: #94a3b8;
}

/* Tables */
thead tr th {
    background-color: #bfdbfe !important;
    color: #1e293b !important;
}

/* Footer */
.footer {
    color: #cbd5e1;
    font-size: 0.9rem;
    text-align: center;
    padding: 2rem;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session state initialization
# -----------------------------------------------------------------------------
if "orchestrator" not in st.session_state:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found in .env file")
        st.stop()

    st.session_state.orchestrator = MedicalIDPOrchestrator(api_key)
    st.session_state.map_generator = MapGenerator()

# -----------------------------------------------------------------------------
# Load dataset (FIXED PATH)
# -----------------------------------------------------------------------------
DATA_PATH = BASE_DIR / "ghana_facilities.csv"

if "facilities_df" not in st.session_state:
    if not DATA_PATH.exists():
        st.error(f"❌ Data file not found at: {DATA_PATH}")
        st.stop()

    st.session_state.facilities_df = pd.read_csv(DATA_PATH)

if "query_history" not in st.session_state:
    st.session_state.query_history = []

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">🏥 Virtue Foundation - Medical IDP Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bridging Medical Deserts Through Intelligent Document Parsing</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🎯 Quick Actions")

    sample_queries = [
        "Which hospitals can perform cardiac surgery in Greater Accra?",
        "Show me medical deserts for pediatric care",
        "Find facilities with CT scan equipment",
        "What are the capability gaps in Northern region?",
        "Identify suspicious facility claims"
    ]

    selected = st.selectbox("Sample Queries", [""] + sample_queries)
    if st.button("Run Sample Query") and selected:
        st.session_state.current_query = selected
        st.rerun()

    st.divider()
    st.metric("Total Facilities", len(st.session_state.facilities_df))
    st.metric("Regions Covered", st.session_state.facilities_df["region"].nunique())

    st.divider()
    show_citations = st.checkbox("Show Citations", value=True)
    show_trace = st.checkbox("Show Agent Trace", value=False)
    show_map = st.checkbox("Generate Map", value=True)

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Query",
    "🗺️ Medical Desert Map",
    "📊 Dashboard",
    "📚 Dataset Explorer"
])

# =============================================================================
# TAB 1 — QUERY
# =============================================================================
with tab1:
    query = st.text_input(
        "Ask a question about medical facilities in Ghana:",
        value=st.session_state.get("current_query", "")
    )

    if st.button("🔍 Search", type="primary") and query:
        with st.spinner("Processing query..."):
            try:
                result = st.session_state.orchestrator.process_query(
                    query, st.session_state.facilities_df
                )

                st.markdown("### 💬 Response")
                st.markdown(result["response"])

                # -------------------------
                # Matching facilities
                # -------------------------
                if result.get("matching_facilities"):
                    st.markdown("### 🏥 Matching Facilities")
                    for i, match in enumerate(result["matching_facilities"][:10], 1):
                        f = match["facility"]
                        with st.expander(f"{i}. {f['facility_name']} ({f['region']})"):
                            st.write(f"**Type:** {f['facility_type']}")
                            st.write(f"**Score:** {f.get('capability_score', 0):.0f}/100")
                            st.write(f"**Confidence:** {match['confidence']:.0%}")
                            if f.get("anomalies"):
                                st.warning("; ".join(f["anomalies"]))

                # -------------------------
                # SAFE analysis handling
                # -------------------------
                analysis = result.get("analysis_results") or {}

                if analysis.get("medical_deserts"):
                    st.markdown("### 🚨 Medical Deserts")
                    for d in analysis["medical_deserts"][:5]:
                        cls = "alert-critical" if d.severity == "critical" else "alert-warning"
                        st.markdown(f"""
                        <div class="{cls}">
                        <strong>{d.region}</strong> – {d.severity.upper()}<br>
                        Missing {len(d.missing_capabilities)} capabilities
                        </div>
                        """, unsafe_allow_html=True)

                if analysis.get("capability_gaps"):
                    st.markdown("### 📉 Capability Gaps")
                    gap_df = pd.DataFrame([{
                        "Capability": g.capability_name,
                        "Type": g.capability_type,
                        "Regions": len(g.regions_affected),
                        "Priority": g.priority
                    } for g in analysis["capability_gaps"][:10]])
                    st.dataframe(gap_df, use_container_width=True)

                # -------------------------
                # Map (Windows safe)
                # -------------------------
                if show_map and result.get("matching_facilities"):
                    map_path = BASE_DIR / "facility_map.html"
                    fmap = st.session_state.map_generator.create_facility_map(
                        [m["facility"] for m in result["matching_facilities"]]
                    )
                    st.session_state.map_generator.save_map(fmap, str(map_path))
                    st.components.v1.html(map_path.read_text(encoding="utf-8"),height=600)


                # -------------------------
                # Extras
                # -------------------------
                st.info(f"⏱️ Processing time: {result['processing_time_ms']:.2f} ms")

                if show_citations and result.get("citations"):
                    with st.expander("📖 Citations"):
                        st.json(result["citations"])

                if show_trace and result.get("citation_report"):
                    with st.expander("🔍 Agent Trace"):
                        st.code(result["citation_report"])

            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)

# =============================================================================
# TAB 2 — MAP
# =============================================================================
with tab2:
    st.header("🗺️ Medical Desert Visualization")
    st.write("Generate a nationwide medical desert map")

    if st.button("Generate Map"):
        with st.spinner("Analyzing..."):
            extractor = ExtractionAgent(os.getenv("ANTHROPIC_API_KEY"))
            extracted = []
            for _, row in st.session_state.facilities_df.iterrows():
                data = extractor.extract_from_facility(row.to_dict())
                data.update({
                    "region": row["region"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"]
                })
                extracted.append(data)

            analysis = AnalysisAgent().analyze_regional_coverage(extracted)
            map_path = BASE_DIR / "desert_map.html"

            desert_map = st.session_state.map_generator.create_desert_map(
                extracted, analysis["medical_deserts"]
            )
            st.session_state.map_generator.save_map(desert_map, str(map_path))
            st.components.v1.html(map_path.read_text(encoding="utf-8"),height=600)

# =============================================================================
# TAB 3 — DASHBOARD
# =============================================================================
with tab3:
    df = st.session_state.facilities_df
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Facilities", len(df))
    c2.metric("Regions", df["region"].nunique())
    c3.metric("Teaching Hospitals", len(df[df["facility_type"] == "Teaching Hospital"]))
    c4.metric("Emergency Services", len(df[df["emergency_services"] == "Yes"]))

    st.bar_chart(df["region"].value_counts())

# =============================================================================
# TAB 4 — DATASET
# =============================================================================
with tab4:
    st.dataframe(st.session_state.facilities_df, use_container_width=True)

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.divider()
st.markdown("""
<div style="text-align:center;color:#7f8c8d;padding:2rem">
<strong>Virtue Foundation – Intelligent Document Parsing Agent</strong><br>
Built for Databricks Hackathon 2025
</div>
""", unsafe_allow_html=True)

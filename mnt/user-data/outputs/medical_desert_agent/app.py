"""
Streamlit Web Interface for Medical Desert Analysis
User-friendly interface for NGO planners to query healthcare data
"""

import streamlit as st
import pandas as pd
from document_parser import parse_facility_dataset, identify_medical_deserts
from agentic_planner import HealthcareAgent, EXAMPLE_QUERIES
from visualization import create_medical_desert_map, create_summary_statistics
import os
from datetime import datetime
import json


# Page configuration
st.set_page_config(
    page_title="Medical Desert Intelligence System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        font-weight: bold;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-top: 0;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        margin-top: 5px;
    }
    .alert-critical {
        background-color: #e74c3c;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-warning {
        background-color: #f39c12;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .citation-box {
        background-color: #ecf0f1;
        padding: 10px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and parse facility data (cached)"""
    data_path = '/home/claude/medical_desert_agent/ghana_facilities.csv'
    if os.path.exists(data_path):
        return parse_facility_dataset(data_path)
    return []


@st.cache_resource
def initialize_agent(_profiles):
    """Initialize the healthcare agent (cached)"""
    return HealthcareAgent(_profiles)


def display_facility_card(profile):
    """Display a facility as a card"""
    
    # Determine risk level color
    risk = profile.desert_risk_score
    if risk >= 75:
        risk_color = "#e74c3c"
        risk_label = "CRITICAL"
    elif risk >= 60:
        risk_color = "#e67e22"
        risk_label = "HIGH"
    elif risk >= 40:
        risk_color = "#f39c12"
        risk_label = "MODERATE"
    else:
        risk_color = "#27ae60"
        risk_label = "LOW"
    
    st.markdown(f"""
    <div style="border: 2px solid {risk_color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
        <h3 style="color: {risk_color}; margin: 0;">{profile.facility_name}</h3>
        <p style="margin: 5px 0;"><b>Type:</b> {profile.facility_type} | <b>Region:</b> {profile.region}</p>
        <p style="margin: 5px 0;">
            <span style="background-color: {risk_color}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">
                {risk_label} RISK: {risk:.0f}/100
            </span>
            <span style="margin-left: 10px;">Capability: {profile.capability_score:.0f}/100</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Specialties:**")
        if profile.specialties:
            for spec in profile.specialties[:5]:
                st.write(f"✓ {spec}")
        else:
            st.write("_None listed_")
    
    with col2:
        st.write("**Equipment:**")
        if profile.equipment:
            for eq in profile.equipment[:5]:
                st.write(f"✓ {eq}")
        else:
            st.write("_None listed_")
    
    with col3:
        st.write("**⚠️ Critical Gaps:**")
        if profile.gaps:
            for gap in profile.gaps[:5]:
                st.write(f"❌ {gap}")
        else:
            st.write("_None identified_")


def main():
    # Header
    st.markdown('<p class="main-header">🏥 Medical Desert Intelligence System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Healthcare Resource Planning for Ghana</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading facility data..."):
        profiles = load_data()
    
    if not profiles:
        st.error("⚠️ No data found. Please ensure ghana_facilities.csv exists.")
        return
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard", "🤖 AI Assistant", "🗺️ Interactive Map", "📋 Facility Explorer", "📈 Reports"]
    )
    
    # Dashboard Page
    if page == "📊 Dashboard":
        st.header("Overview Dashboard")
        
        # Statistics
        stats = create_summary_statistics(profiles)
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-value">{stats['risk_distribution']['critical']}</div>
                <div class="stat-label">CRITICAL RISK</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <div class="stat-value">{stats['risk_distribution']['high']}</div>
                <div class="stat-label">HIGH RISK</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
                <div class="stat-value">{stats['total_facilities']}</div>
                <div class="stat-label">TOTAL FACILITIES</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                <div class="stat-value">{stats['avg_desert_risk']:.0f}/100</div>
                <div class="stat-label">AVG DESERT RISK</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Regional breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Highest Risk Regions")
            sorted_regions = sorted(
                stats['regional_stats'].items(),
                key=lambda x: x[1]['avg_desert_risk'],
                reverse=True
            )
            
            for region, data in sorted_regions[:5]:
                risk = data['avg_desert_risk']
                if risk >= 70:
                    alert_class = "alert-critical"
                elif risk >= 50:
                    alert_class = "alert-warning"
                else:
                    alert_class = ""
                
                if alert_class:
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <b>{region}</b><br>
                        Risk Score: {risk:.1f} | {data['count']} facilities | {data['total_gaps']} gaps
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(f"**{region}** - Risk: {risk:.1f} | {data['count']} facilities")
        
        with col2:
            st.subheader("🔧 Most Critical Gaps")
            for gap in stats['top_gaps'][:5]:
                st.warning(f"**{gap['gap']}** - Affects {gap['count']} facilities")
    
    # AI Assistant Page
    elif page == "🤖 AI Assistant":
        st.header("AI Healthcare Planning Assistant")
        st.write("Ask questions in natural language about healthcare resources in Ghana")
        
        # Initialize agent
        agent = initialize_agent(profiles)
        
        # Example queries
        st.subheader("💡 Try these questions:")
        example_cols = st.columns(2)
        for i, example in enumerate(EXAMPLE_QUERIES):
            with example_cols[i % 2]:
                if st.button(example, key=f"example_{i}"):
                    st.session_state['query'] = example
        
        # Query input
        query = st.text_input(
            "Your question:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., Which regions need more surgeons?"
        )
        
        if st.button("🔍 Analyze", type="primary"):
            if query:
                with st.spinner("AI agent analyzing... This may take a moment."):
                    result = agent.run(query)
                
                # Display answer
                st.markdown("### 📝 Analysis Result")
                st.markdown(result['answer'])
                
                # Show recommendations
                if result['recommendations']:
                    st.markdown("### 🎯 Recommended Actions")
                    for i, rec in enumerate(result['recommendations'], 1):
                        priority_color = "#e74c3c" if rec['priority'] == 'HIGH' else "#f39c12"
                        st.markdown(f"""
                        <div style="border-left: 4px solid {priority_color}; padding-left: 15px; margin: 10px 0;">
                            <b>{i}. [{rec['priority']}] {rec.get('action', rec.get('region', 'Action'))}</b><br>
                            <small>{rec.get('rationale', '')}</small><br>
                            <small><i>Impact: {rec.get('impact', '')}</i></small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show reasoning steps with citations
                with st.expander("🔬 View Reasoning Steps & Citations"):
                    for step in result['reasoning_steps']:
                        st.markdown(f"""
                        <div class="citation-box">
                            <b>Step {step['step']}: {step['action']}</b><br>
                            <i>Thought:</i> {step['thought']}<br>
                            <i>Data Used:</i> {', '.join(step['data_used'][:3])}<br>
                            <i>Citations:</i> {', '.join(step['citations'][:3])}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a question")
    
    # Interactive Map Page
    elif page == "🗺️ Interactive Map":
        st.header("Interactive Medical Desert Map")
        
        with st.spinner("Generating map..."):
            map_path = create_medical_desert_map(profiles, '/tmp/medical_desert_map.html')
        
        # Display map
        with open(map_path, 'r') as f:
            map_html = f.read()
        
        st.components.v1.html(map_html, height=600, scrolling=True)
        
        # Download button
        st.download_button(
            label="📥 Download Map",
            data=map_html,
            file_name="medical_desert_map.html",
            mime="text/html"
        )
    
    # Facility Explorer
    elif page == "📋 Facility Explorer":
        st.header("Facility Explorer")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            regions = list(set(p.region for p in profiles))
            selected_region = st.selectbox("Filter by Region", ["All"] + sorted(regions))
        
        with col2:
            risk_filter = st.selectbox(
                "Filter by Risk Level",
                ["All", "Critical (75+)", "High (60-74)", "Moderate (40-59)", "Low (<40)"]
            )
        
        with col3:
            facility_types = list(set(p.facility_type for p in profiles))
            selected_type = st.selectbox("Filter by Type", ["All"] + sorted(facility_types))
        
        # Apply filters
        filtered = profiles
        
        if selected_region != "All":
            filtered = [p for p in filtered if p.region == selected_region]
        
        if selected_type != "All":
            filtered = [p for p in filtered if p.facility_type == selected_type]
        
        if risk_filter != "All":
            if "Critical" in risk_filter:
                filtered = [p for p in filtered if p.desert_risk_score >= 75]
            elif "High" in risk_filter:
                filtered = [p for p in filtered if 60 <= p.desert_risk_score < 75]
            elif "Moderate" in risk_filter:
                filtered = [p for p in filtered if 40 <= p.desert_risk_score < 60]
            elif "Low" in risk_filter:
                filtered = [p for p in filtered if p.desert_risk_score < 40]
        
        st.write(f"**Showing {len(filtered)} of {len(profiles)} facilities**")
        
        # Display facilities
        for profile in sorted(filtered, key=lambda x: x.desert_risk_score, reverse=True):
            display_facility_card(profile)
    
    # Reports Page
    elif page == "📈 Reports":
        st.header("Reports & Analytics")
        
        # Identify medical deserts
        deserts = identify_medical_deserts(profiles, threshold=60.0)
        
        st.subheader("🚨 Identified Medical Desert Regions")
        st.write(f"Found {len(deserts)} regions at high risk")
        
        for desert in deserts:
            st.markdown(f"""
            <div class="alert-critical">
                <h3>{desert['region']}</h3>
                <p><b>Desert Risk Score:</b> {desert['desert_risk_score']:.1f}/100</p>
                <p><b>Facilities:</b> {desert['facility_count']} | <b>Total Gaps:</b> {desert['total_gaps']}</p>
                <p><b>Critical Issues:</b></p>
                <ul>
                    {''.join([f'<li>{gap}</li>' for gap in desert['critical_gaps'][:5]])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Export options
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as CSV
            export_data = []
            for p in profiles:
                export_data.append({
                    'Facility ID': p.facility_id,
                    'Name': p.facility_name,
                    'Region': p.region,
                    'Type': p.facility_type,
                    'Desert Risk Score': p.desert_risk_score,
                    'Capability Score': p.capability_score,
                    'Specialties': ', '.join(p.specialties),
                    'Gaps': ', '.join(p.gaps)
                })
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="Download Full Analysis (CSV)",
                data=csv,
                file_name=f"ghana_medical_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export desert regions as JSON
            json_data = json.dumps(deserts, indent=2)
            st.download_button(
                label="Download Desert Regions (JSON)",
                data=json_data,
                file_name=f"medical_deserts_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()

"""
Main Execution Script for Medical Desert Intelligence System
Runs the complete pipeline: parsing → reasoning → visualization
"""

import sys
import os
from datetime import datetime
from document_parser import parse_facility_dataset, identify_medical_deserts
from agentic_planner import HealthcareAgent
from visualization import create_medical_desert_map, generate_regional_report, create_summary_statistics
from mlflow_tracking import track_agent_execution, create_experiment_dashboard
import json


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print(" 🏥 MEDICAL DESERT INTELLIGENCE SYSTEM")
    print(" Building Healthcare Coordination for the Virtue Foundation")
    print("="*70 + "\n")


def run_complete_analysis(data_path: str = 'ghana_facilities.csv', 
                         interactive: bool = False):
    """
    Run complete analysis pipeline
    
    Args:
        data_path: Path to facility CSV data
        interactive: If True, prompts for user queries
    """
    
    print_banner()
    
    # Step 1: Parse facility data
    print("📊 STEP 1: Parsing Facility Data")
    print("-" * 70)
    
    full_path = f'/home/claude/medical_desert_agent/{data_path}'
    if not os.path.exists(full_path):
        print(f"❌ Error: Data file not found at {full_path}")
        return
    
    profiles = parse_facility_dataset(full_path)
    print(f"✅ Parsed {len(profiles)} facilities from dataset")
    
    # Show sample
    sample = profiles[0]
    print(f"\n📋 Sample Extraction - {sample.facility_name}:")
    print(f"   - Capability Score: {sample.capability_score:.1f}/100")
    print(f"   - Desert Risk Score: {sample.desert_risk_score:.1f}/100")
    print(f"   - Specialties: {len(sample.specialties)}")
    print(f"   - Equipment: {len(sample.equipment)}")
    print(f"   - Identified Gaps: {len(sample.gaps)}")
    
    if sample.capabilities:
        print(f"   - Total Capabilities Extracted: {len(sample.capabilities)}")
        print(f"   - Example Capability: {sample.capabilities[0].name} ({sample.capabilities[0].capability_type})")
    
    # Step 2: Identify medical deserts
    print(f"\n\n🚨 STEP 2: Identifying Medical Deserts")
    print("-" * 70)
    
    deserts = identify_medical_deserts(profiles, threshold=60.0)
    print(f"✅ Identified {len(deserts)} high-risk regions\n")
    
    if deserts:
        print("High-Risk Regions:")
        for i, desert in enumerate(deserts, 1):
            print(f"   {i}. {desert['region']}")
            print(f"      → Risk Score: {desert['desert_risk_score']:.1f}/100")
            print(f"      → {desert['facility_count']} facilities, {desert['total_gaps']} total gaps")
            print(f"      → Top Gap: {desert['critical_gaps'][0] if desert['critical_gaps'] else 'N/A'}")
    
    # Step 3: Run AI Agent Analysis
    print(f"\n\n🤖 STEP 3: AI Agent Analysis")
    print("-" * 70)
    
    agent = HealthcareAgent(profiles)
    
    # Default query or interactive
    if interactive:
        print("\nEnter your query (or press Enter for default):")
        query = input("> ").strip()
        if not query:
            query = "Which regions in Ghana are medical deserts and need urgent intervention?"
    else:
        query = "Which regions in Ghana are medical deserts and need urgent intervention?"
    
    print(f"\n🔍 Query: {query}")
    print("⏳ Agent reasoning...\n")
    
    # Track with MLflow
    result = track_agent_execution(agent, query, profiles)
    
    print("\n" + "="*70)
    print("AGENT ANALYSIS COMPLETE")
    print("="*70)
    print(result['answer'])
    
    # Show reasoning steps with citations
    print("\n\n📚 REASONING STEPS & CITATIONS:")
    print("-" * 70)
    for step in result['reasoning_steps']:
        print(f"\nStep {step['step']}: {step['action']}")
        print(f"  💭 Thought: {step['thought']}")
        print(f"  📊 Data Used: {', '.join(step['data_used'][:3])}")
        print(f"  📎 Citations: {', '.join(step['citations'][:3])}")
    
    print(f"\n⏱️  Execution Time: {result['execution_time']:.2f} seconds")
    print(f"🔬 MLflow Run ID: {result['run_id']}")
    
    # Step 4: Create Visualizations
    print(f"\n\n🗺️  STEP 4: Creating Visualizations")
    print("-" * 70)
    
    # Create map
    map_path = create_medical_desert_map(profiles, 'medical_desert_map.html')
    print(f"✅ Interactive map created: {map_path}")
    
    # Create report
    report_path = generate_regional_report(profiles, 'regional_report.html')
    print(f"✅ Regional report created: {report_path}")
    
    # Step 5: Generate Summary Statistics
    print(f"\n\n📈 STEP 5: Summary Statistics")
    print("-" * 70)
    
    stats = create_summary_statistics(profiles)
    
    print(f"\n🏥 Total Facilities: {stats['total_facilities']}")
    print(f"\n📊 Risk Distribution:")
    print(f"   - Critical (75+):  {stats['risk_distribution']['critical']} facilities")
    print(f"   - High (60-74):    {stats['risk_distribution']['high']} facilities")
    print(f"   - Moderate (40-59): {stats['risk_distribution']['moderate']} facilities")
    print(f"   - Low (<40):       {stats['risk_distribution']['low']} facilities")
    
    print(f"\n🌍 Regional Overview:")
    sorted_regions = sorted(
        stats['regional_stats'].items(),
        key=lambda x: x[1]['avg_desert_risk'],
        reverse=True
    )
    for region, data in sorted_regions[:5]:
        print(f"   {region:20} → Risk: {data['avg_desert_risk']:5.1f} | Facilities: {data['count']} | Gaps: {data['total_gaps']}")
    
    print(f"\n🔧 Top 5 Critical Gaps:")
    for i, gap in enumerate(stats['top_gaps'][:5], 1):
        print(f"   {i}. {gap['gap']}")
        print(f"      → Affects {gap['count']} facilities")
    
    # Step 6: Export Results
    print(f"\n\n💾 STEP 6: Exporting Results")
    print("-" * 70)
    
    # Export desert analysis
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'medical_deserts': deserts,
        'summary_stats': stats,
        'recommendations': result.get('recommendations', [])
    }
    
    export_path = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Analysis results exported: {export_path}")
    
    # Final summary
    print("\n\n" + "="*70)
    print("✨ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n📁 Generated Files:")
    print(f"   1. {map_path} - Interactive medical desert map")
    print(f"   2. {report_path} - Regional analysis report")
    print(f"   3. {export_path} - Complete analysis data (JSON)")
    print(f"\n🚀 Next Steps:")
    print(f"   - Open {map_path} in browser to explore interactive map")
    print(f"   - Review {report_path} for detailed regional breakdown")
    print(f"   - Run 'python app.py' to launch web interface")
    print(f"   - Use MLflow UI to view experiment tracking")
    print("\n" + "="*70 + "\n")


def run_web_interface():
    """Launch the Streamlit web interface"""
    print_banner()
    print("🚀 Launching Web Interface...")
    print("="*70)
    print("\nThe web interface will open in your browser.")
    print("If it doesn't open automatically, navigate to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server.\n")
    
    os.system("streamlit run app.py")


def show_help():
    """Show help information"""
    print_banner()
    print("USAGE:")
    print("  python main.py [command] [options]\n")
    print("COMMANDS:")
    print("  analyze     - Run complete analysis pipeline (default)")
    print("  web         - Launch web interface")
    print("  experiments - Show MLflow experiment dashboard")
    print("  help        - Show this help message\n")
    print("OPTIONS:")
    print("  --interactive  - Enable interactive query mode\n")
    print("EXAMPLES:")
    print("  python main.py")
    print("  python main.py analyze --interactive")
    print("  python main.py web")
    print("  python main.py experiments")
    print()


if __name__ == "__main__":
    # Parse command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    interactive = "--interactive" in sys.argv
    
    if command == "analyze":
        run_complete_analysis(interactive=interactive)
    
    elif command == "web":
        run_web_interface()
    
    elif command == "experiments":
        print_banner()
        create_experiment_dashboard()
    
    elif command == "help":
        show_help()
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py help' for usage information")

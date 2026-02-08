#!/usr/bin/env python3
"""
Demo Script - Command Line Interface for Virtue Foundation IDP Agent
Run queries without the web interface
"""

import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from orchestrator import MedicalIDPOrchestrator
from extraction_agent import ExtractionAgent
from analysis_agent import AnalysisAgent


# Load environment
load_dotenv()

def print_header():
    """Print demo header"""
    print("=" * 80)
    print("VIRTUE FOUNDATION - INTELLIGENT DOCUMENT PARSING AGENT")
    print("Bridging Medical Deserts Through AI")
    print("=" * 80)
    print()

def print_result(result):
    """Pretty print query results"""
    print("\n" + "─" * 80)
    print("RESPONSE:")
    analysis = result.get('analysis_results') or {}
    print("─" * 80)
    print(result['response'])
    print()
    
    # Show matching facilities
    if result.get('matching_facilities'):
        print("\n" + "─" * 80)
        print(f"MATCHING FACILITIES: {len(result['matching_facilities'])}")
        print("─" * 80)
        
        for i, match in enumerate(result['matching_facilities'][:5], 1):
            facility = match['facility']
            print(f"\n{i}. {facility['facility_name']}")
            print(f"   Region: {facility['region']}")
            print(f"   Type: {facility['facility_type']}")
            print(f"   Capability Score: {facility.get('capability_score', 0):.0f}/100")
            print(f"   Confidence: {match['confidence']:.0%}")
            
            if facility.get('anomalies'):
                print(f"   ⚠️  Issues: {'; '.join(facility['anomalies'][:2])}")
    
    # Normalize analysis results ONCE
    analysis = result.get('analysis_results') or {}

    # Show medical deserts
    if analysis.get('medical_deserts'):
        deserts = analysis['medical_deserts']
        print("\n" + "─" * 80)
        print(f"MEDICAL DESERTS: {len(deserts)}")
        print("─" * 80)
        
        for desert in deserts[:5]:
            severity_symbol = {
                'critical': '🔴',
                'severe': '🟠',
                'moderate': '🟡'
            }.get(desert.severity, '⚪')
            
            print(f"\n{severity_symbol} {desert.region} - {desert.severity.upper()}")
            print(f"   Missing {len(desert.missing_capabilities)} capabilities")
            if desert.missing_capabilities:
                print(f"   Top gaps: {', '.join(desert.missing_capabilities[:3])}")

    # Show capability gaps
    if analysis.get('capability_gaps'):
        gaps = analysis['capability_gaps']
        print("\n" + "─" * 80)
        print(f"CAPABILITY GAPS: {len(gaps)}")
        print("─" * 80)
        
        for gap in gaps[:5]:
            print(f"\n• {gap.capability_name} ({gap.capability_type})")
            print(f"  Priority: {gap.priority.upper()}")
            print(f"  Regions affected: {len(gap.regions_affected)}")

    
    # Show processing time
    print("\n" + "─" * 80)
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
    print("─" * 80)

def run_demo():
    """Run interactive demo"""
    print_header()
    
    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in .env file")
        return
    
    # Load data
    print("Loading Ghana facilities data...")
    data_path = Path(__file__).parent / 'ghana_facilities.csv'
    
    if not data_path.exists():
        print(f"❌ ERROR: Data file not found at {data_path}")
        return
    
    facilities_df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(facilities_df)} facilities from {len(facilities_df['region'].unique())} regions\n")
    
    # Initialize orchestrator
    print("Initializing AI agents...")
    orchestrator = MedicalIDPOrchestrator(api_key)
    print("✓ Agents ready\n")
    
    # Sample queries
    sample_queries = [
        "Which hospitals can perform cardiac surgery in Greater Accra?",
        "Show me medical deserts for emergency care",
        "Find facilities with CT scan equipment",
        "What are the capability gaps in Northern region?",
        "Identify suspicious facility claims"
    ]
    
    print("SAMPLE QUERIES:")
    for i, query in enumerate(sample_queries, 1):
        print(f"{i}. {query}")
    print(f"{len(sample_queries) + 1}. Custom query")
    print("0. Exit")
    print()
    
    while True:
        try:
            choice = input("Select a query (0-6): ").strip()
            
            if choice == '0':
                print("\nThank you for using Virtue Foundation IDP Agent!")
                break
            
            if choice == str(len(sample_queries) + 1):
                query = input("\nEnter your query: ").strip()
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(sample_queries):
                        query = sample_queries[idx]
                    else:
                        print("Invalid choice. Please try again.")
                        continue
                except ValueError:
                    print("Invalid choice. Please try again.")
                    continue
            
            if not query:
                print("Empty query. Please try again.")
                continue
            
            print(f"\n{'=' * 80}")
            print(f"PROCESSING QUERY: {query}")
            print('=' * 80)
            print("\nThinking...")
            
            # Process query
            result = orchestrator.process_query(query, facilities_df)
            
            # Display result
            print_result(result)
            
            # Ask if user wants to see citations
            show_citations = input("\nShow detailed citations? (y/n): ").strip().lower()
            if show_citations == 'y':
                print("\n" + "=" * 80)
                print("CITATION TRACE")
                print("=" * 80)
                print(result['citation_report'])
            
            print("\n" + "=" * 80)
            print()
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("Please try another query.\n")

def run_single_query(query: str):
    """Run a single query and print results"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found")
        return
    
    data_path = Path(__file__).parent / 'data' / 'ghana_facilities.csv'
    facilities_df = pd.read_csv(data_path)
    
    orchestrator = MedicalIDPOrchestrator(api_key)
    
    print(f"\nProcessing: {query}\n")
    result = orchestrator.process_query(query, facilities_df)
    print_result(result)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run with command line argument
        query = ' '.join(sys.argv[1:])
        run_single_query(query)
    else:
        # Run interactive demo
        run_demo()

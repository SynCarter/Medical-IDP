#!/usr/bin/env python3
"""
Standalone Demo of Medical Desert Intelligence System
Works without external dependencies - demonstrates core concepts
"""

import json
import csv
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import re


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class MedicalCapability:
    """A single medical capability with citation"""
    capability_type: str
    name: str
    status: str
    confidence: float
    source_text: str
    facility_id: str


@dataclass
class FacilityProfile:
    """Complete profile of a medical facility"""
    facility_id: str
    facility_name: str
    region: str
    district: str
    coordinates: Tuple[float, float]
    facility_type: str
    specialties: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    procedures: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    urgent_needs: List[str] = field(default_factory=list)
    capabilities: List[MedicalCapability] = field(default_factory=list)
    capability_score: float = 0.0
    desert_risk_score: float = 0.0


# ============================================================================
# DOCUMENT PARSER
# ============================================================================

class SimpleDocumentParser:
    """Simplified document parser for demo"""
    
    def parse_csv(self, filepath: str) -> List[FacilityProfile]:
        """Parse facility CSV file"""
        profiles = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                profile = self._parse_facility(row)
                profiles.append(profile)
        
        return profiles
    
    def _parse_facility(self, row: Dict) -> FacilityProfile:
        """Parse a single facility record"""
        facility_id = row['facility_id']
        
        # Create profile
        profile = FacilityProfile(
            facility_id=facility_id,
            facility_name=row['facility_name'],
            region=row['region'],
            district=row['district'],
            coordinates=(float(row['latitude']), float(row['longitude'])),
            facility_type=row['facility_type']
        )
        
        # Parse structured fields
        if row['specialties']:
            profile.specialties = [s.strip() for s in row['specialties'].split(',')]
        
        if row['equipment']:
            profile.equipment = [e.strip() for e in row['equipment'].split(',')]
        
        if row['procedures']:
            profile.procedures = [p.strip() for p in row['procedures'].split(',')]
        
        # Extract from staff notes
        notes = row.get('staff_notes', '')
        if notes:
            self._extract_gaps(profile, notes)
        
        # Compute scores
        self._compute_scores(profile)
        
        return profile
    
    def _extract_gaps(self, profile: FacilityProfile, notes: str):
        """Extract capability gaps from notes"""
        notes_lower = notes.lower()
        
        # Detect shortages
        if 'no ' in notes_lower or 'need more' in notes_lower:
            # Simple extraction
            if 'no surgeon' in notes_lower or 'no neurosurgeon' in notes_lower:
                profile.gaps.append("Missing surgeon")
            
            if 'need more' in notes_lower:
                profile.gaps.append("Staff shortage")
            
            if 'broke down' in notes_lower or 'broken' in notes_lower:
                profile.gaps.append("Broken equipment")
        
        # Detect limited resources
        if 'limited' in notes_lower or 'only' in notes_lower:
            profile.gaps.append("Limited resources")
    
    def _compute_scores(self, profile: FacilityProfile):
        """Compute capability and risk scores"""
        # Capability score
        base_score = (
            len(profile.specialties) * 5 +
            len(profile.equipment) * 3 +
            len(profile.procedures) * 2
        )
        
        type_multiplier = {
            'Teaching Hospital': 1.0,
            'Regional Hospital': 0.7,
            'District Hospital': 0.4,
            'Mission Hospital': 0.5
        }.get(profile.facility_type, 0.3)
        
        profile.capability_score = min(100, base_score * type_multiplier)
        
        # Desert risk score
        risk = 0
        
        if profile.capability_score < 30:
            risk += 30
        elif profile.capability_score < 50:
            risk += 15
        
        risk += min(30, len(profile.gaps) * 10)
        
        profile.desert_risk_score = min(100, risk)


# ============================================================================
# SIMPLE AGENT
# ============================================================================

class SimpleHealthcareAgent:
    """Simplified reasoning agent for demo"""
    
    def __init__(self, profiles: List[FacilityProfile]):
        self.profiles = profiles
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze a query and generate response"""
        query_lower = query.lower()
        
        result = {
            'query': query,
            'findings': [],
            'recommendations': [],
            'reasoning_steps': []
        }
        
        # Step 1: Understand query
        if 'desert' in query_lower or 'underserved' in query_lower:
            query_type = 'medical_desert'
        elif 'surgeon' in query_lower or 'doctor' in query_lower:
            query_type = 'staffing'
        else:
            query_type = 'general'
        
        result['reasoning_steps'].append({
            'step': 1,
            'action': 'Query Classification',
            'result': f'Classified as {query_type} query'
        })
        
        # Step 2: Gather data
        if query_type == 'medical_desert':
            high_risk = [p for p in self.profiles if p.desert_risk_score >= 60]
            result['findings'].append(f"Found {len(high_risk)} high-risk facilities")
            
            # Group by region
            regions = {}
            for p in high_risk:
                if p.region not in regions:
                    regions[p.region] = []
                regions[p.region].append(p)
            
            result['reasoning_steps'].append({
                'step': 2,
                'action': 'Data Gathering',
                'result': f'Analyzed {len(regions)} regions with high risk'
            })
            
            # Generate recommendations
            for region, facilities in sorted(regions.items(), key=lambda x: len(x[1]), reverse=True):
                avg_risk = sum(f.desert_risk_score for f in facilities) / len(facilities)
                
                result['recommendations'].append({
                    'region': region,
                    'priority': 'HIGH' if avg_risk >= 70 else 'MEDIUM',
                    'action': f'Deploy resources to {region}',
                    'rationale': f'{len(facilities)} facilities at risk (avg: {avg_risk:.0f}/100)'
                })
        
        elif query_type == 'staffing':
            with_gaps = [p for p in self.profiles if p.gaps]
            result['findings'].append(f"Found {len(with_gaps)} facilities with staffing gaps")
            
            result['reasoning_steps'].append({
                'step': 2,
                'action': 'Data Gathering',
                'result': f'Identified {len(with_gaps)} facilities needing staff'
            })
        
        return result


# ============================================================================
# DEMO RUNNER
# ============================================================================

def run_demo():
    """Run the complete demo"""
    print("\n" + "="*70)
    print(" 🏥 MEDICAL DESERT INTELLIGENCE SYSTEM - DEMO")
    print("="*70 + "\n")
    
    # Step 1: Parse data
    print("📊 Step 1: Parsing Facility Data")
    print("-" * 70)
    
    parser = SimpleDocumentParser()
    profiles = parser.parse_csv('ghana_facilities.csv')
    
    print(f"✅ Parsed {len(profiles)} facilities\n")
    
    # Show sample
    sample = profiles[0]
    print(f"Sample Facility: {sample.facility_name}")
    print(f"  Region: {sample.region}")
    print(f"  Type: {sample.facility_type}")
    print(f"  Capability Score: {sample.capability_score:.1f}/100")
    print(f"  Desert Risk Score: {sample.desert_risk_score:.1f}/100")
    print(f"  Specialties: {len(sample.specialties)}")
    print(f"  Equipment: {len(sample.equipment)}")
    print(f"  Gaps: {len(sample.gaps)}")
    
    # Step 2: Identify deserts
    print(f"\n\n🚨 Step 2: Identifying Medical Deserts")
    print("-" * 70)
    
    high_risk = [p for p in profiles if p.desert_risk_score >= 60]
    critical = [p for p in profiles if p.desert_risk_score >= 75]
    
    print(f"✅ Risk Analysis:")
    print(f"  Critical Risk (75+): {len(critical)} facilities")
    print(f"  High Risk (60-74): {len(high_risk) - len(critical)} facilities")
    print(f"  Total High Risk: {len(high_risk)} facilities\n")
    
    if high_risk:
        print("Highest Risk Facilities:")
        for p in sorted(high_risk, key=lambda x: x.desert_risk_score, reverse=True)[:5]:
            print(f"  • {p.facility_name} ({p.region}): {p.desert_risk_score:.0f}/100")
    
    # Step 3: Run AI agent
    print(f"\n\n🤖 Step 3: AI Agent Analysis")
    print("-" * 70)
    
    agent = SimpleHealthcareAgent(profiles)
    
    query = "Which regions in Ghana are medical deserts?"
    print(f"\nQuery: {query}\n")
    
    result = agent.analyze(query)
    
    print("Reasoning Steps:")
    for step in result['reasoning_steps']:
        print(f"  Step {step['step']}: {step['action']}")
        print(f"    → {step['result']}")
    
    print(f"\n📋 Findings:")
    for finding in result['findings']:
        print(f"  • {finding}")
    
    print(f"\n🎯 Recommendations:")
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"  {i}. [{rec['priority']}] {rec['action']}")
        print(f"     Rationale: {rec['rationale']}")
    
    # Step 4: Regional summary
    print(f"\n\n📈 Step 4: Regional Summary")
    print("-" * 70)
    
    regions = {}
    for p in profiles:
        if p.region not in regions:
            regions[p.region] = {
                'count': 0,
                'total_risk': 0,
                'total_capability': 0,
                'gaps': 0
            }
        
        regions[p.region]['count'] += 1
        regions[p.region]['total_risk'] += p.desert_risk_score
        regions[p.region]['total_capability'] += p.capability_score
        regions[p.region]['gaps'] += len(p.gaps)
    
    print("\nRegion Overview (sorted by risk):\n")
    print(f"{'Region':<25} {'Facilities':<12} {'Avg Risk':<12} {'Total Gaps':<12}")
    print("-" * 70)
    
    for region in sorted(regions.keys(), 
                        key=lambda r: regions[r]['total_risk']/regions[r]['count'], 
                        reverse=True):
        data = regions[region]
        avg_risk = data['total_risk'] / data['count']
        
        print(f"{region:<25} {data['count']:<12} {avg_risk:<12.1f} {data['gaps']:<12}")
    
    # Summary
    print("\n\n" + "="*70)
    print(" ✨ DEMO COMPLETE")
    print("="*70)
    print("\nThis demo showed:")
    print("  ✅ Document parsing from unstructured text")
    print("  ✅ Intelligent capability extraction")
    print("  ✅ Medical desert identification")
    print("  ✅ Multi-step agentic reasoning")
    print("  ✅ Regional analysis and recommendations")
    print("\nFull system features:")
    print("  • Interactive web interface (Streamlit)")
    print("  • Visual maps (Folium)")
    print("  • MLflow experiment tracking")
    print("  • Citation tracking at each step")
    print("  • Natural language queries")
    print("\nTo run the full system:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run: python main.py analyze")
    print("  3. Or launch web UI: streamlit run app.py")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    run_demo()

"""
Intelligent Document Parser for Medical Facilities
Extracts structured medical capabilities from unstructured text
"""

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
import pandas as pd


class MedicalCapability(BaseModel):
    """Extracted medical capability with citation"""
    capability_type: str = Field(description="Type: specialty, equipment, procedure, or staffing")
    name: str = Field(description="Name of the capability")
    status: str = Field(description="Status: available, limited, unavailable, or broken")
    confidence: float = Field(description="Confidence score 0-1")
    source_text: str = Field(description="Original text this was extracted from")
    facility_id: str = Field(description="Source facility ID")


class FacilityProfile(BaseModel):
    """Complete profile of a medical facility"""
    facility_id: str
    facility_name: str
    region: str
    district: str
    coordinates: tuple[float, float]
    facility_type: str
    
    # Extracted capabilities
    specialties: List[str] = []
    equipment: List[str] = []
    procedures: List[str] = []
    
    # Critical issues
    gaps: List[str] = []
    urgent_needs: List[str] = []
    suspicious_claims: List[str] = []
    
    # All extracted capabilities with citations
    capabilities: List[MedicalCapability] = []
    
    # Computed metrics
    capability_score: float = 0.0
    desert_risk_score: float = 0.0


@dataclass
class ExtractionStep:
    """Citation tracking for each extraction step"""
    step_number: int
    agent_action: str
    input_data: str
    output_result: str
    source_rows: List[str]
    timestamp: str


class IntelligentDocumentParser:
    """
    Parses unstructured medical facility data using pattern matching
    and rule-based extraction (can be upgraded to LLM-based)
    """
    
    def __init__(self):
        # Medical terminology patterns
        self.specialty_patterns = [
            r'cardiology', r'neurosurgery', r'oncology', r'pediatrics',
            r'orthopedics', r'obstetrics', r'internal medicine', r'emergency',
            r'ophthalmology', r'dentistry', r'general medicine', r'surgery'
        ]
        
        self.equipment_patterns = [
            r'MRI', r'CT [Ss]canner', r'X-[Rr]ay', r'[Uu]ltrasound',
            r'ventilator', r'ICU', r'operating theater', r'catheterization lab',
            r'blood bank', r'laboratory', r'ambulance'
        ]
        
        self.procedure_patterns = [
            r'surgery', r'cesarean', r'chemotherapy', r'dialysis',
            r'trauma care', r'intensive care', r'delivery', r'deliveries',
            r'immunization', r'vaccination', r'transplant'
        ]
        
        # Negative indicators
        self.shortage_patterns = [
            r'short on', r'need more', r'no (.*?) available',
            r'limited (.*?)', r'broke down', r'awaiting replacement',
            r'struggling with', r'only \d+ (.*?) on staff'
        ]
        
        self.citation_log: List[ExtractionStep] = []
        
    def extract_capabilities(self, row: pd.Series) -> FacilityProfile:
        """
        Extract all medical capabilities from a facility record
        Returns a complete facility profile with citations
        """
        facility_id = row['facility_id']
        
        # Initialize profile
        profile = FacilityProfile(
            facility_id=facility_id,
            facility_name=row['facility_name'],
            region=row['region'],
            district=row['district'],
            coordinates=(row['latitude'], row['longitude']),
            facility_type=row['facility_type']
        )
        
        # Combine all text fields for analysis
        text_fields = {
            'specialties': str(row.get('specialties', '')),
            'equipment': str(row.get('equipment', '')),
            'procedures': str(row.get('procedures', '')),
            'staff_notes': str(row.get('staff_notes', ''))
        }
        
        combined_text = ' '.join(text_fields.values())
        
        # Step 1: Extract structured fields
        self._extract_structured_fields(profile, text_fields, facility_id)
        
        # Step 2: Extract capabilities from unstructured notes
        self._extract_from_notes(profile, text_fields['staff_notes'], facility_id)
        
        # Step 3: Detect gaps and issues
        self._detect_gaps(profile, combined_text, facility_id)
        
        # Step 4: Compute scores
        self._compute_scores(profile)
        
        return profile
    
    def _extract_structured_fields(self, profile: FacilityProfile, 
                                   text_fields: Dict[str, str], 
                                   facility_id: str):
        """Extract from structured CSV columns"""
        
        # Parse specialties
        if text_fields['specialties']:
            specialties = [s.strip() for s in text_fields['specialties'].split(',')]
            profile.specialties = specialties
            
            for spec in specialties:
                profile.capabilities.append(MedicalCapability(
                    capability_type="specialty",
                    name=spec,
                    status="available",
                    confidence=0.95,
                    source_text=text_fields['specialties'],
                    facility_id=facility_id
                ))
        
        # Parse equipment
        if text_fields['equipment']:
            equipment = [e.strip() for e in text_fields['equipment'].split(',')]
            profile.equipment = equipment
            
            for eq in equipment:
                profile.capabilities.append(MedicalCapability(
                    capability_type="equipment",
                    name=eq,
                    status="available",
                    confidence=0.95,
                    source_text=text_fields['equipment'],
                    facility_id=facility_id
                ))
        
        # Parse procedures
        if text_fields['procedures']:
            procedures = [p.strip() for p in text_fields['procedures'].split(',')]
            profile.procedures = procedures
            
            for proc in procedures:
                profile.capabilities.append(MedicalCapability(
                    capability_type="procedure",
                    name=proc,
                    status="available",
                    confidence=0.95,
                    source_text=text_fields['procedures'],
                    facility_id=facility_id
                ))
    
    def _extract_from_notes(self, profile: FacilityProfile, 
                           notes: str, 
                           facility_id: str):
        """Extract additional capabilities mentioned in unstructured notes"""
        
        if not notes or notes == 'nan':
            return
        
        notes_lower = notes.lower()
        
        # Extract specialties mentioned in notes
        for pattern in self.specialty_patterns:
            matches = re.finditer(pattern, notes_lower, re.IGNORECASE)
            for match in matches:
                specialty = match.group(0)
                if specialty not in [s.lower() for s in profile.specialties]:
                    profile.capabilities.append(MedicalCapability(
                        capability_type="specialty",
                        name=specialty.title(),
                        status="mentioned",
                        confidence=0.7,
                        source_text=notes,
                        facility_id=facility_id
                    ))
        
        # Extract equipment mentioned in notes
        for pattern in self.equipment_patterns:
            matches = re.finditer(pattern, notes_lower, re.IGNORECASE)
            for match in matches:
                equipment = match.group(0)
                
                # Check status context
                context_start = max(0, match.start() - 50)
                context_end = min(len(notes), match.end() + 50)
                context = notes[context_start:context_end].lower()
                
                if 'broke' in context or 'broken' in context or 'not working' in context:
                    status = "broken"
                elif 'no ' + equipment.lower() in context:
                    status = "unavailable"
                else:
                    status = "available"
                
                profile.capabilities.append(MedicalCapability(
                    capability_type="equipment",
                    name=equipment,
                    status=status,
                    confidence=0.8,
                    source_text=context,
                    facility_id=facility_id
                ))
    
    def _detect_gaps(self, profile: FacilityProfile, 
                     text: str, 
                     facility_id: str):
        """Detect capability gaps and urgent needs"""
        
        text_lower = text.lower()
        
        # Detect shortages
        shortage_indicators = [
            (r'short on (.*?)[\.,]', 'Staff shortage: {}'),
            (r'need more (.*?)[\.,]', 'Urgent need: {}'),
            (r'no (.*?) available', 'Missing: {}'),
            (r'no (.*?) on (permanent )?staff', 'No {} on staff'),
            (r'only (\d+) (.*?) on staff', 'Limited {}: only {} available'),
        ]
        
        for pattern, template in shortage_indicators:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if len(match.groups()) == 1:
                    gap = template.format(match.group(1).strip())
                else:
                    gap = template.format(match.group(2).strip(), match.group(1))
                profile.gaps.append(gap)
                profile.urgent_needs.append(gap)
        
        # Detect broken/unavailable critical equipment
        critical_equipment = ['CT scanner', 'MRI', 'ICU', 'operating theater']
        for equip in critical_equipment:
            equip_lower = equip.lower()
            if equip_lower in text_lower:
                # Check for negative context
                if re.search(f'no {equip_lower}', text_lower):
                    profile.gaps.append(f"No {equip}")
                elif re.search(f'{equip_lower}.*?broke', text_lower):
                    profile.gaps.append(f"{equip} broken/awaiting repair")
        
        # Detect suspicious claims (facility type vs capabilities mismatch)
        if profile.facility_type == "District Hospital":
            advanced_equipment = ['MRI', 'CT Scanner', 'Cardiac Catheterization']
            for eq in advanced_equipment:
                if any(eq.lower() in e.lower() for e in profile.equipment):
                    profile.suspicious_claims.append(
                        f"District hospital claims {eq} - verify accuracy"
                    )
    
    def _compute_scores(self, profile: FacilityProfile):
        """Compute capability and desert risk scores"""
        
        # Capability score based on available resources
        specialty_count = len(profile.specialties)
        equipment_count = len(profile.equipment)
        procedure_count = len(profile.procedures)
        
        # Weight by facility type
        type_weights = {
            "Teaching Hospital": 1.0,
            "Regional Hospital": 0.7,
            "District Hospital": 0.4,
            "Mission Hospital": 0.5
        }
        base_weight = type_weights.get(profile.facility_type, 0.3)
        
        # Compute capability score (0-100)
        profile.capability_score = min(100, (
            (specialty_count * 5) + 
            (equipment_count * 3) + 
            (procedure_count * 2)
        ) * base_weight)
        
        # Desert risk score - higher = more likely to be in medical desert
        desert_factors = 0
        
        # Factor 1: Low capability score
        if profile.capability_score < 30:
            desert_factors += 30
        elif profile.capability_score < 50:
            desert_factors += 15
        
        # Factor 2: Number of gaps
        desert_factors += min(30, len(profile.gaps) * 5)
        
        # Factor 3: Critical missing equipment
        critical_missing = ['CT Scanner', 'MRI', 'ICU', 'Operating Theater']
        for critical in critical_missing:
            if not any(critical.lower() in eq.lower() for eq in profile.equipment):
                desert_factors += 10
        
        profile.desert_risk_score = min(100, desert_factors)


def parse_facility_dataset(csv_path: str) -> List[FacilityProfile]:
    """
    Parse entire facility dataset and extract all capabilities
    """
    df = pd.read_csv(csv_path)
    parser = IntelligentDocumentParser()
    
    profiles = []
    for _, row in df.iterrows():
        profile = parser.extract_capabilities(row)
        profiles.append(profile)
    
    return profiles


def identify_medical_deserts(profiles: List[FacilityProfile], 
                            threshold: float = 60.0) -> List[Dict[str, Any]]:
    """
    Identify regions at high risk of being medical deserts
    """
    deserts = []
    
    # Group by region
    region_data = {}
    for profile in profiles:
        region = profile.region
        if region not in region_data:
            region_data[region] = []
        region_data[region].append(profile)
    
    # Analyze each region
    for region, facilities in region_data.items():
        avg_desert_score = sum(f.desert_risk_score for f in facilities) / len(facilities)
        avg_capability = sum(f.capability_score for f in facilities) / len(facilities)
        
        total_gaps = sum(len(f.gaps) for f in facilities)
        
        if avg_desert_score >= threshold:
            deserts.append({
                'region': region,
                'desert_risk_score': avg_desert_score,
                'avg_capability_score': avg_capability,
                'facility_count': len(facilities),
                'total_gaps': total_gaps,
                'facilities': [f.facility_name for f in facilities],
                'critical_gaps': list(set([gap for f in facilities for gap in f.gaps]))
            })
    
    return sorted(deserts, key=lambda x: x['desert_risk_score'], reverse=True)


if __name__ == "__main__":
    # Test the parser
    profiles = parse_facility_dataset('/home/claude/medical_desert_agent/ghana_facilities.csv')
    
    print(f"Parsed {len(profiles)} facilities\n")
    
    # Show sample extraction
    sample = profiles[0]
    print(f"Sample: {sample.facility_name}")
    print(f"Capability Score: {sample.capability_score:.1f}")
    print(f"Desert Risk Score: {sample.desert_risk_score:.1f}")
    print(f"Specialties: {', '.join(sample.specialties[:3])}")
    print(f"Gaps: {sample.gaps[:2]}")
    print(f"\nExtracted {len(sample.capabilities)} capabilities with citations")
    
    # Identify deserts
    deserts = identify_medical_deserts(profiles)
    print(f"\n\nIdentified {len(deserts)} medical desert regions:")
    for desert in deserts:
        print(f"  - {desert['region']}: Risk={desert['desert_risk_score']:.1f}, {desert['facility_count']} facilities")

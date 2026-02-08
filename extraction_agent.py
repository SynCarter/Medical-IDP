"""
Extraction Agent - Intelligent Document Parsing
Extracts structured information from free-text medical facility descriptions
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import anthropic
import os


@dataclass
class ExtractedCapability:
    """Structured representation of a medical capability"""
    capability_type: str  # 'procedure', 'equipment', 'specialty'
    name: str
    details: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None  # 'operational', 'broken', 'claimed'
    confidence: float = 1.0


class ExtractionAgent:
    """
    Parses unstructured medical facility data to extract:
    - Medical procedures and their volumes
    - Equipment types, quantities, and operational status
    - Medical specialties and staffing levels
    - Capability gaps and anomalies
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        
        # Predefined medical vocabularies for pattern matching
        self.procedure_keywords = {
            'cardiac surgery', 'neurosurgery', 'transplantation', 'cesarean',
            'appendectomy', 'hernia repair', 'fracture management', 'laparoscopic',
            'cataract surgery', 'joint replacement', 'bypass', 'valve replacement',
            'cleft repair', 'orthopedic', 'trauma surgery'
        }
        
        self.equipment_keywords = {
            'mri', 'ct scanner', 'x-ray', 'ultrasound', 'ventilator', 
            'operating theater', 'icu', 'dialysis', 'catheterization lab',
            'blood bank', 'mammography', 'endoscopy', 'autoclave'
        }
        
        self.specialty_keywords = {
            'cardiology', 'neurology', 'orthopedics', 'obstetrics', 'gynecology',
            'pediatrics', 'oncology', 'nephrology', 'emergency medicine',
            'ophthalmology', 'surgery', 'internal medicine'
        }
    
    def extract_from_facility(self, facility_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured capabilities from a single facility record
        
        Args:
            facility_data: Dictionary containing facility information
            
        Returns:
            Dictionary with extracted capabilities and anomalies
        """
        procedures_text = facility_data.get('procedures_free_text', '')
        equipment_text = facility_data.get('equipment_free_text', '')
        specialties_text = facility_data.get('specialties_free_text', '')
        
        # Extract using both rule-based and LLM methods
        procedures = self._extract_procedures(procedures_text)
        equipment = self._extract_equipment(equipment_text)
        specialties = self._extract_specialties(specialties_text)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(
            procedures, equipment, specialties, facility_data
        )
        
        return {
            'facility_id': facility_data.get('facility_id'),
            'facility_name': facility_data.get('facility_name'),
            'procedures': procedures,
            'equipment': equipment,
            'specialties': specialties,
            'anomalies': anomalies,
            'capability_score': self._calculate_capability_score(procedures, equipment, specialties)
        }
    
    def _extract_procedures(self, text: str) -> List[ExtractedCapability]:
        """Extract medical procedures from free text"""
        if not text:
            return []
        
        procedures = []
        text_lower = text.lower()
        
        # Rule-based extraction for known procedures
        for procedure in self.procedure_keywords:
            if procedure in text_lower:
                # Extract context around the procedure
                details = self._extract_context(text, procedure)
                
                # Try to extract volume/frequency
                volume = self._extract_volume(text, procedure)
                
                procedures.append(ExtractedCapability(
                    capability_type='procedure',
                    name=procedure.title(),
                    details=details,
                    quantity=volume,
                    confidence=0.9
                ))
        
        # Use LLM for more nuanced extraction
        llm_procedures = self._llm_extract_procedures(text)
        procedures.extend(llm_procedures)
        
        return self._deduplicate_capabilities(procedures)
    
    def _extract_equipment(self, text: str) -> List[ExtractedCapability]:
        """Extract medical equipment from free text"""
        if not text:
            return []
        
        equipment = []
        text_lower = text.lower()
        
        # Look for equipment with quantities and status
        for equip in self.equipment_keywords:
            if equip in text_lower:
                quantity = self._extract_quantity(text, equip)
                status = self._extract_status(text, equip)
                
                equipment.append(ExtractedCapability(
                    capability_type='equipment',
                    name=equip.upper() if len(equip) <= 3 else equip.title(),
                    quantity=quantity,
                    status=status or 'operational',
                    confidence=0.85
                ))
        
        return self._deduplicate_capabilities(equipment)
    
    def _extract_specialties(self, text: str) -> List[ExtractedCapability]:
        """Extract medical specialties from free text"""
        if not text:
            return []
        
        specialties = []
        text_lower = text.lower()
        
        for specialty in self.specialty_keywords:
            if specialty in text_lower:
                details = self._extract_context(text, specialty)
                
                specialties.append(ExtractedCapability(
                    capability_type='specialty',
                    name=specialty.title(),
                    details=details,
                    confidence=0.9
                ))
        
        return self._deduplicate_capabilities(specialties)
    
    def _llm_extract_procedures(self, text: str) -> List[ExtractedCapability]:
        """Use Claude to extract procedures not caught by rules"""
        if not text or len(text) < 20:
            return []
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": f"""Extract all medical procedures from this text. For each procedure, identify:
1. Procedure name
2. Any volume/frequency mentioned
3. Complexity level if indicated

Text: {text}

Respond in JSON format:
[{{"name": "procedure_name", "volume": number or null, "complexity": "basic/advanced/specialized" or null}}]

If no procedures found, return empty array []."""
                }]
            )
            
            response_text = message.content[0].text.strip()
            
            # Parse JSON response (simplified - real implementation would be more robust)
            import json
            try:
                procedures_data = json.loads(response_text)
                return [
                    ExtractedCapability(
                        capability_type='procedure',
                        name=p['name'],
                        quantity=p.get('volume'),
                        details=p.get('complexity'),
                        confidence=0.8
                    )
                    for p in procedures_data
                ]
            except:
                return []
                
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return []
    
    def _extract_context(self, text: str, keyword: str, window: int = 50) -> str:
        """Extract context around a keyword"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        pos = text_lower.find(keyword_lower)
        if pos == -1:
            return ""
        
        start = max(0, pos - window)
        end = min(len(text), pos + len(keyword) + window)
        
        return text[start:end].strip()
    
    def _extract_volume(self, text: str, procedure: str) -> Optional[int]:
        """Extract procedure volume from text"""
        # Look for patterns like "200 cardiac surgeries", "approximately 150 major surgeries"
        context = self._extract_context(text, procedure, 100)
        
        # Pattern: number + procedure
        volume_pattern = r'(\d+)\s*(?:major\s+)?(?:surgeries|procedures|operations)'
        match = re.search(volume_pattern, context.lower())
        
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_quantity(self, text: str, equipment: str) -> Optional[int]:
        """Extract equipment quantity from text"""
        context = self._extract_context(text, equipment, 30)
        
        # Pattern: number + equipment or equipment (number)
        qty_pattern = r'(\d+)\s*(?:tesla\s+)?' + re.escape(equipment)
        match = re.search(qty_pattern, context.lower())
        
        if match:
            return int(match.group(1))
        
        # Alternative pattern: equipment (number units)
        alt_pattern = re.escape(equipment) + r'\s*\((\d+)\s*(?:units?|machines?)?\)'
        match = re.search(alt_pattern, context.lower())
        
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_status(self, text: str, equipment: str) -> Optional[str]:
        """Extract equipment operational status"""
        context = self._extract_context(text, equipment, 60).lower()
        
        if any(word in context for word in ['broken', 'not working', 'non-functional', 'out of order']):
            return 'broken'
        elif any(word in context for word in ['claimed', 'claims to have', 'not verified']):
            return 'claimed'
        
        return 'operational'
    
    def _detect_anomalies(
        self,
        procedures: List[ExtractedCapability],
        equipment: List[ExtractedCapability],
        specialties: List[ExtractedCapability],
        facility_data: Dict[str, Any]
    ) -> List[str]:
        """Detect suspicious claims or capability gaps"""
        anomalies = []
        
        # Check for advanced procedures without supporting equipment
        advanced_procedures = {'cardiac surgery', 'neurosurgery', 'transplantation'}
        procedure_names = {p.name.lower() for p in procedures}
        equipment_names = {e.name.lower() for e in equipment}
        
        if 'cardiac surgery' in procedure_names:
            required = ['ct scanner', 'icu']
            missing = [r for r in required if not any(r in e for e in equipment_names)]
            if missing:
                anomalies.append(f"Claims cardiac surgery but missing: {', '.join(missing)}")
        
        # Check for broken equipment
        broken_equipment = [e.name for e in equipment if e.status == 'broken']
        if broken_equipment:
            anomalies.append(f"Non-functional equipment: {', '.join(broken_equipment)}")
        
        # Check for claimed but unverified capabilities
        claimed = [e.name for e in equipment if e.status == 'claimed']
        if claimed:
            anomalies.append(f"Unverified claims: {', '.join(claimed)}")
        
        # Check for procedures without matching specialties
        if 'cardiac surgery' in procedure_names:
            if not any('cardio' in s.name.lower() for s in specialties):
                anomalies.append("Claims cardiac surgery but no cardiology specialty listed")
        
        return anomalies
    
    def _calculate_capability_score(
        self,
        procedures: List[ExtractedCapability],
        equipment: List[ExtractedCapability],
        specialties: List[ExtractedCapability]
    ) -> float:
        """Calculate overall capability score (0-100)"""
        score = 0.0
        
        # Weight components
        operational_equipment = [e for e in equipment if e.status == 'operational']
        score += len(operational_equipment) * 3
        score += len(procedures) * 5
        score += len(specialties) * 4
        
        # Cap at 100
        return min(100.0, score)
    
    def _deduplicate_capabilities(self, capabilities: List[ExtractedCapability]) -> List[ExtractedCapability]:
        """Remove duplicate capabilities, keeping highest confidence"""
        seen = {}
        
        for cap in capabilities:
            key = cap.name.lower()
            if key not in seen or cap.confidence > seen[key].confidence:
                seen[key] = cap
        
        return list(seen.values())

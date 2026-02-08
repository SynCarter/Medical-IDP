"""
Citation Tracker - Tracks data sources used in each agent reasoning step
Provides row-level and step-level citations for transparency
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Citation:
    """Individual citation linking a claim to source data"""
    source_type: str  # 'facility_row', 'aggregation', 'inference'
    facility_id: Optional[str] = None
    facility_name: Optional[str] = None
    field_name: Optional[str] = None
    field_value: Optional[str] = None
    row_number: Optional[int] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_type': self.source_type,
            'facility_id': self.facility_id,
            'facility_name': self.facility_name,
            'field_name': self.field_name,
            'field_value': self.field_value,
            'row_number': self.row_number,
            'confidence': self.confidence
        }


@dataclass
class AgentStep:
    """Records a single reasoning step in the agent workflow"""
    step_number: int
    step_name: str  # e.g., 'query_parsing', 'data_extraction', 'gap_analysis'
    step_description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    citations: List[Citation] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: Optional[float] = None
    
    def add_citation(self, citation: Citation):
        """Add a citation to this step"""
        self.citations.append(citation)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_number': self.step_number,
            'step_name': self.step_name,
            'step_description': self.step_description,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'citations': [c.to_dict() for c in self.citations],
            'timestamp': self.timestamp,
            'duration_ms': self.duration_ms
        }


class CitationTracker:
    """Tracks citations across all agent steps"""
    
    def __init__(self):
        self.steps: List[AgentStep] = []
        self.current_step_number = 0
    
    def start_step(self, step_name: str, step_description: str, input_data: Dict[str, Any]) -> int:
        """Start tracking a new agent step"""
        self.current_step_number += 1
        step = AgentStep(
            step_number=self.current_step_number,
            step_name=step_name,
            step_description=step_description,
            input_data=input_data,
            output_data={}
        )
        self.steps.append(step)
        return self.current_step_number
    
    def end_step(self, step_number: int, output_data: Dict[str, Any], duration_ms: Optional[float] = None):
        """Complete a step with output data"""
        step = self._get_step(step_number)
        if step:
            step.output_data = output_data
            step.duration_ms = duration_ms
    
    def add_citation_to_step(self, step_number: int, citation: Citation):
        """Add a citation to a specific step"""
        step = self._get_step(step_number)
        if step:
            step.add_citation(citation)
    
    def add_facility_citation(
        self,
        step_number: int,
        facility_id: str,
        facility_name: str,
        field_name: str,
        field_value: str,
        row_number: int,
        confidence: float = 1.0
    ):
        """Convenience method to add a facility row citation"""
        citation = Citation(
            source_type='facility_row',
            facility_id=facility_id,
            facility_name=facility_name,
            field_name=field_name,
            field_value=field_value,
            row_number=row_number,
            confidence=confidence
        )
        self.add_citation_to_step(step_number, citation)
    
    def _get_step(self, step_number: int) -> Optional[AgentStep]:
        """Get a step by its number"""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None
    
    def get_all_citations(self) -> List[Citation]:
        """Get all citations across all steps"""
        all_citations = []
        for step in self.steps:
            all_citations.extend(step.citations)
        return all_citations
    
    def get_citations_by_facility(self, facility_id: str) -> List[Citation]:
        """Get all citations for a specific facility"""
        return [
            c for c in self.get_all_citations()
            if c.facility_id == facility_id
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export full trace as dictionary"""
        return {
            'total_steps': len(self.steps),
            'steps': [step.to_dict() for step in self.steps],
            'total_citations': len(self.get_all_citations())
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export trace as JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def generate_citation_report(self) -> str:
        """Generate a human-readable citation report"""
        report = ["=" * 80]
        report.append("AGENT EXECUTION TRACE WITH CITATIONS")
        report.append("=" * 80)
        report.append(f"\nTotal Steps: {len(self.steps)}")
        report.append(f"Total Citations: {len(self.get_all_citations())}\n")
        
        for step in self.steps:
            report.append(f"\n{'─' * 80}")
            report.append(f"Step {step.step_number}: {step.step_name}")
            report.append(f"{'─' * 80}")
            report.append(f"Description: {step.step_description}")
            report.append(f"Timestamp: {step.timestamp}")
            if step.duration_ms:
                report.append(f"Duration: {step.duration_ms:.2f}ms")
            
            report.append(f"\nInput: {json.dumps(step.input_data, indent=2)}")
            report.append(f"\nOutput: {json.dumps(step.output_data, indent=2)}")
            
            if step.citations:
                report.append(f"\nCitations ({len(step.citations)}):")
                for i, citation in enumerate(step.citations, 1):
                    report.append(f"  [{i}] {citation.source_type}")
                    if citation.facility_name:
                        report.append(f"      Facility: {citation.facility_name} ({citation.facility_id})")
                    if citation.field_name:
                        report.append(f"      Field: {citation.field_name}")
                        report.append(f"      Value: {citation.field_value[:100]}...")
                    report.append(f"      Confidence: {citation.confidence:.2f}")
            else:
                report.append("\nNo citations for this step")
        
        report.append(f"\n{'=' * 80}\n")
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    tracker = CitationTracker()
    
    # Step 1: Query parsing
    step1 = tracker.start_step(
        "query_parsing",
        "Parse user query to identify intent and entities",
        {"query": "Which hospitals can perform cardiac surgery in Greater Accra?"}
    )
    tracker.end_step(step1, {
        "intent": "find_facilities_by_capability",
        "procedure": "cardiac surgery",
        "region": "Greater Accra"
    })
    
    # Step 2: Data extraction
    step2 = tracker.start_step(
        "data_extraction",
        "Extract relevant facilities from database",
        {"region": "Greater Accra", "procedure": "cardiac surgery"}
    )
    
    tracker.add_facility_citation(
        step2,
        facility_id="FAC001",
        facility_name="Korle Bu Teaching Hospital",
        field_name="procedures_free_text",
        field_value="Advanced cardiac surgery including bypass and valve replacement",
        row_number=1
    )
    
    tracker.end_step(step2, {"facilities_found": 1})
    
    # Generate report
    print(tracker.generate_citation_report())

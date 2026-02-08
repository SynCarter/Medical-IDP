"""
Orchestrator - LangGraph-based Agent Coordination
Coordinates extraction, analysis, and response generation
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
import pandas as pd
import json
import time

from extraction_agent import ExtractionAgent, ExtractedCapability
from analysis_agent import AnalysisAgent, MedicalDesert, CapabilityGap
from citation_tracker import CitationTracker, Citation

class AgentState(TypedDict):
    """State passed between agents in the graph"""
    # Input
    query: str
    raw_facilities_data: List[Dict[str, Any]]
    
    # Query understanding
    intent: Optional[str]
    entities: Optional[Dict[str, Any]]
    
    # Extracted data
    extracted_facilities: List[Dict[str, Any]]
    
    # Analysis results
    analysis_results: Optional[Dict[str, Any]]
    matching_facilities: List[Dict[str, Any]]
    
    # Output
    response: Optional[str]
    visualizations: Optional[Dict[str, Any]]
    
    # Citation tracking
    citation_tracker: Optional[CitationTracker]
    
    # Metadata
    processing_time_ms: float
    errors: List[str]


class MedicalIDPOrchestrator:
    """
    Orchestrates the full IDP pipeline using LangGraph
    
    Workflow:
    1. Query Understanding: Parse user intent and extract entities
    2. Data Extraction: Extract structured capabilities from facilities
    3. Analysis: Identify gaps, deserts, and matches
    4. Response Generation: Create natural language response
    5. Visualization: Generate maps and charts
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.extraction_agent = ExtractionAgent(api_key)
        self.analysis_agent = AnalysisAgent()
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand_query", self._understand_query_node)
        workflow.add_node("extract_capabilities", self._extract_capabilities_node)
        workflow.add_node("analyze_data", self._analyze_data_node)
        workflow.add_node("generate_response", self._generate_response_node)
        
        # Add edges
        workflow.set_entry_point("understand_query")
        workflow.add_edge("understand_query", "extract_capabilities")
        workflow.add_edge("extract_capabilities", "analyze_data")
        workflow.add_edge("analyze_data", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def process_query(
        self,
        query: str,
        facilities_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Process a natural language query about medical facilities
        
        Args:
            query: User's natural language question
            facilities_df: DataFrame of facility data
            
        Returns:
            Dictionary with response, analysis, and citations
        """
        start_time = time.time()
        
        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "raw_facilities_data": facilities_df.to_dict('records'),
            "intent": None,
            "entities": None,
            "extracted_facilities": [],
            "analysis_results": None,
            "matching_facilities": [],
            "response": None,
            "visualizations": None,
            "citation_tracker": CitationTracker(),
            "processing_time_ms": 0.0,
            "errors": []
        }
        
        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)
            
            # Calculate processing time
            final_state["processing_time_ms"] = (time.time() - start_time) * 1000
            
            return self._format_output(final_state)
            
        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "processing_time_ms": (time.time() - start_time) * 1000
            }
    
    def _understand_query_node(self, state: AgentState) -> AgentState:
        """Node 1: Parse query to understand intent and entities"""
        tracker = state["citation_tracker"]
        step_id = tracker.start_step(
            "query_understanding",
            "Parse natural language query to identify intent and extract entities",
            {"query": state["query"]}
        )
        
        query = state["query"].lower()
        
        # Simple intent classification
        if any(word in query for word in ['which', 'what', 'find', 'show', 'list']):
            if 'gap' in query or 'missing' in query or 'lack' in query:
                intent = 'identify_gaps'
            elif 'desert' in query:
                intent = 'find_medical_deserts'
            else:
                intent = 'find_facilities'
        elif 'analyze' in query or 'coverage' in query:
            intent = 'analyze_coverage'
        else:
            intent = 'general_query'
        
        # Extract entities (simplified - real implementation would use NER)
        entities = {}
        
        # Extract region
        regions = ['greater accra', 'ashanti', 'northern', 'western', 'volta', 
                  'central', 'eastern', 'upper east', 'upper west']
        for region in regions:
            if region in query:
                entities['region'] = region.title()
                break
        
        # Extract capability/procedure
        procedures = ['cardiac surgery', 'neurosurgery', 'cesarean', 'dialysis', 
                     'transplant', 'icu', 'ct scan', 'mri']
        for proc in procedures:
            if proc in query:
                entities['capability'] = proc
                break
        
        state["intent"] = intent
        state["entities"] = entities
        
        tracker.end_step(step_id, {
            "intent": intent,
            "entities": entities
        })
        
        return state
    
    def _extract_capabilities_node(self, state: AgentState) -> AgentState:
        """Node 2: Extract structured capabilities from all facilities"""
        tracker = state["citation_tracker"]
        step_id = tracker.start_step(
            "capability_extraction",
            "Extract structured medical capabilities from unstructured facility text",
            {"facility_count": len(state["raw_facilities_data"])}
        )
        
        extracted_facilities = []
        
        for i, facility in enumerate(state["raw_facilities_data"]):
            extracted = self.extraction_agent.extract_from_facility(facility)
            
            # Add original data
            extracted.update({
                'region': facility.get('region'),
                'district': facility.get('district'),
                'facility_type': facility.get('facility_type'),
                'latitude': facility.get('latitude'),
                'longitude': facility.get('longitude'),
                'bed_capacity': facility.get('bed_capacity'),
                'staff_count': facility.get('staff_count')
            })
            
            extracted_facilities.append(extracted)
            
            # Add citations for extracted data
            for proc in extracted.get('procedures', []):
                tracker.add_facility_citation(
                    step_id,
                    facility_id=facility['facility_id'],
                    facility_name=facility['facility_name'],
                    field_name='procedures_free_text',
                    field_value=facility.get('procedures_free_text', '')[:100],
                    row_number=i + 1,
                    confidence=proc.confidence
                )
        
        state["extracted_facilities"] = extracted_facilities
        
        tracker.end_step(step_id, {
            "extracted_count": len(extracted_facilities),
            "total_procedures": sum(len(f.get('procedures', [])) for f in extracted_facilities),
            "total_equipment": sum(len(f.get('equipment', [])) for f in extracted_facilities)
        })
        
        return state
    
    def _analyze_data_node(self, state: AgentState) -> AgentState:
        """Node 3: Analyze data based on query intent"""
        tracker = state["citation_tracker"]
        step_id = tracker.start_step(
            "data_analysis",
            f"Analyze facilities for intent: {state['intent']}",
            {
                "intent": state["intent"],
                "entities": state["entities"]
            }
        )
        
        intent = state["intent"]
        entities = state["entities"]
        facilities = state["extracted_facilities"]
        
        if intent == 'find_facilities':
            # Find facilities matching capability
            capability = entities.get('capability', '')
            region = entities.get('region')
            
            matches = self.analysis_agent.find_facilities_by_capability(
                facilities, capability, region
            )
            
            state["matching_facilities"] = matches
            
            # Add citations for matches
            for match in matches:
                tracker.add_facility_citation(
                    step_id,
                    facility_id=match['facility']['facility_id'],
                    facility_name=match['facility']['facility_name'],
                    field_name=match['match_type'],
                    field_value=match['match_name'],
                    row_number=0,  # Would need to track this
                    confidence=match['confidence']
                )
        
        elif intent in ['identify_gaps', 'find_medical_deserts', 'analyze_coverage']:
            # Run full regional analysis
            analysis = self.analysis_agent.analyze_regional_coverage(facilities)
            state["analysis_results"] = analysis
        
        else:
            # General analysis
            analysis = self.analysis_agent.analyze_regional_coverage(facilities)
            state["analysis_results"] = analysis
        
        tracker.end_step(step_id, {
            "matches_found": len(state.get("matching_facilities", [])),
            "analysis_completed": state["analysis_results"] is not None
        })
        
        return state
    
    def _generate_response_node(self, state: AgentState) -> AgentState:
        """Node 4: Generate natural language response"""
        tracker = state["citation_tracker"]
        step_id = tracker.start_step(
            "response_generation",
            "Generate natural language response to user query",
            {"intent": state["intent"]}
        )
        
        intent = state["intent"]
        
        if intent == 'find_facilities' and state.get("matching_facilities"):
            response = self._generate_facility_match_response(state)
        
        elif intent == 'find_medical_deserts' and state.get("analysis_results"):
            response = self._generate_desert_response(state)
        
        elif intent == 'identify_gaps' and state.get("analysis_results"):
            response = self._generate_gap_response(state)
        
        elif state.get("analysis_results"):
            response = self._generate_coverage_response(state)
        
        else:
            response = "I couldn't find relevant information for your query."
        
        state["response"] = response
        
        tracker.end_step(step_id, {
            "response_length": len(response),
            "response_type": intent
        })
        
        return state
    
    def _generate_facility_match_response(self, state: AgentState) -> str:
        """Generate response for facility search queries"""
        matches = state["matching_facilities"]
        entities = state["entities"]
        capability = entities.get('capability', 'the requested capability')
        
        if not matches:
            return f"No facilities found with {capability}."
        
        lines = [f"Found {len(matches)} facility/facilities with {capability}:\n"]
        
        for i, match in enumerate(matches[:5], 1):  # Top 5
            facility = match['facility']
            name = facility['facility_name']
            region = facility['region']
            ftype = facility['facility_type']
            confidence = match['confidence']
            
            line = f"{i}. **{name}** ({ftype}, {region})"
            
            if match.get('status'):
                line += f" - Equipment status: {match['status']}"
            
            if match.get('details'):
                line += f"\n   Details: {match['details']}"
            
            if confidence < 0.8:
                line += f" ⚠️ (Confidence: {confidence:.0%})"
            
            lines.append(line)
        
        if len(matches) > 5:
            lines.append(f"\n...and {len(matches) - 5} more facilities")
        
        return "\n".join(lines)
    
    def _generate_desert_response(self, state: AgentState) -> str:
        """Generate response about medical deserts"""
        analysis = state["analysis_results"]
        deserts = analysis.get("medical_deserts", [])
        
        if not deserts:
            return "No critical medical deserts identified. All regions have basic healthcare coverage."
        
        lines = [f"**Medical Desert Analysis**\n"]
        lines.append(f"Identified {len(deserts)} underserved regions:\n")
        
        for desert in deserts[:5]:
            severity_emoji = {
                'critical': '🔴',
                'severe': '🟠',
                'moderate': '🟡'
            }.get(desert.severity, '⚪')
            
            lines.append(f"{severity_emoji} **{desert.region}** - {desert.severity.upper()}")
            lines.append(f"   Missing capabilities: {len(desert.missing_capabilities)}")
            
            if desert.missing_capabilities:
                top_missing = desert.missing_capabilities[:3]
                lines.append(f"   - {', '.join(top_missing)}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_gap_response(self, state: AgentState) -> str:
        """Generate response about capability gaps"""
        analysis = state["analysis_results"]
        gaps = analysis.get("capability_gaps", [])
        
        if not gaps:
            return "No significant capability gaps identified."
        
        lines = ["**Capability Gap Analysis**\n"]
        
        critical_gaps = [g for g in gaps if g.priority == 'critical']
        if critical_gaps:
            lines.append("Critical Gaps:")
            for gap in critical_gaps[:3]:
                lines.append(
                    f"- **{gap.capability_name}**: Missing in {len(gap.regions_affected)} regions"
                )
        
        high_gaps = [g for g in gaps if g.priority == 'high']
        if high_gaps:
            lines.append("\nHigh Priority Gaps:")
            for gap in high_gaps[:3]:
                lines.append(
                    f"- {gap.capability_name}: {len(gap.regions_affected)} regions affected"
                )
        
        return "\n".join(lines)
    
    def _generate_coverage_response(self, state: AgentState) -> str:
        """Generate general coverage analysis response"""
        analysis = state["analysis_results"]
        stats = analysis.get("coverage_statistics", {})
        
        lines = ["**Healthcare Coverage Analysis**\n"]
        lines.append(f"Total Facilities: {stats.get('total_facilities', 0)}")
        lines.append(f"Average Capability Score: {stats.get('average_capability_score', 0)}/100")
        lines.append(f"Facilities with Issues: {stats.get('facilities_with_anomalies', 0)}\n")
        
        # Add recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            lines.append("**Key Recommendations:**")
            for rec in recommendations[:3]:
                lines.append(f"- {rec}")
        
        return "\n".join(lines)
    
    def _format_output(self, state: AgentState) -> Dict[str, Any]:
        """Format final output for user"""
        return {
            "query": state["query"],
            "response": state["response"],
            "intent": state["intent"],
            "entities": state["entities"],
            "matching_facilities": state.get("matching_facilities", []),
            "analysis_results": state.get("analysis_results"),
            "citations": state["citation_tracker"].to_dict(),
            "citation_report": state["citation_tracker"].generate_citation_report(),
            "processing_time_ms": state["processing_time_ms"],
            "errors": state["errors"]
        }

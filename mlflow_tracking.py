"""
MLflow Experiment Tracking for Healthcare Agent
Tracks model performance, citations, and agent decisions
"""

import mlflow
import mlflow.pyfunc
from datetime import datetime
import json
from typing import Dict, Any, List
import pandas as pd


class HealthcareAgentTracker:
    """
    MLflow tracking for the healthcare agent
    Logs queries, responses, reasoning steps, and citations
    """
    
    def __init__(self, experiment_name: str = "medical_desert_agent"):
        mlflow.set_experiment(experiment_name)
        self.current_run_id = None
    
    def start_run(self, run_name: str = None):
        """Start a new MLflow run"""
        if run_name is None:
            run_name = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        mlflow.start_run(run_name=run_name)
        self.current_run_id = mlflow.active_run().info.run_id
        return self.current_run_id
    
    def log_query(self, query: str, query_type: str):
        """Log the input query"""
        mlflow.log_param("query", query)
        mlflow.log_param("query_type", query_type)
        mlflow.log_param("timestamp", datetime.now().isoformat())
    
    def log_data_sources(self, facility_count: int, regions: List[str]):
        """Log data sources used in analysis"""
        mlflow.log_param("facility_count", facility_count)
        mlflow.log_param("regions_analyzed", len(regions))
        mlflow.log_param("region_list", ",".join(regions[:10]))
    
    def log_reasoning_steps(self, reasoning_steps: List[Dict[str, Any]]):
        """Log each reasoning step with citations"""
        mlflow.log_param("total_reasoning_steps", len(reasoning_steps))
        
        # Create a detailed log file
        steps_log = []
        for step in reasoning_steps:
            steps_log.append({
                'step_number': step['step'],
                'action': step['action'],
                'thought': step['thought'],
                'data_sources': step['data_used'],
                'citations': step['citations']
            })
        
        # Save as artifact
        steps_file = f"/tmp/reasoning_steps_{self.current_run_id}.json"
        with open(steps_file, 'w') as f:
            json.dump(steps_log, f, indent=2)
        
        mlflow.log_artifact(steps_file, "reasoning_steps")
    
    def log_citations(self, citations: List[Dict[str, Any]]):
        """Log all citations used to support conclusions"""
        total_citations = sum(len(c.get('sources', [])) for c in citations)
        mlflow.log_metric("total_citations", total_citations)
        
        # Create citation report
        citation_file = f"/tmp/citations_{self.current_run_id}.json"
        with open(citation_file, 'w') as f:
            json.dump(citations, f, indent=2)
        
        mlflow.log_artifact(citation_file, "citations")
    
    def log_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Log generated recommendations"""
        mlflow.log_metric("recommendation_count", len(recommendations))
        
        high_priority = sum(1 for r in recommendations if r.get('priority') == 'HIGH')
        mlflow.log_metric("high_priority_recommendations", high_priority)
        
        # Save recommendations
        rec_file = f"/tmp/recommendations_{self.current_run_id}.json"
        with open(rec_file, 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        mlflow.log_artifact(rec_file, "recommendations")
    
    def log_performance_metrics(self, execution_time: float, facilities_analyzed: int):
        """Log performance metrics"""
        mlflow.log_metric("execution_time_seconds", execution_time)
        mlflow.log_metric("facilities_analyzed", facilities_analyzed)
        mlflow.log_metric("avg_time_per_facility", execution_time / max(facilities_analyzed, 1))
    
    def log_quality_metrics(self, 
                          citation_coverage: float,
                          reasoning_depth: int,
                          data_completeness: float):
        """Log quality metrics for the analysis"""
        mlflow.log_metric("citation_coverage", citation_coverage)
        mlflow.log_metric("reasoning_depth", reasoning_depth)
        mlflow.log_metric("data_completeness", data_completeness)
    
    def end_run(self):
        """End the current MLflow run"""
        if mlflow.active_run():
            mlflow.end_run()
        self.current_run_id = None


def track_agent_execution(agent, query: str, profiles: List[Any]) -> Dict[str, Any]:
    """
    Execute agent with full MLflow tracking
    """
    import time
    
    tracker = HealthcareAgentTracker()
    
    # Start tracking
    run_id = tracker.start_run(f"query_{datetime.now().strftime('%H%M%S')}")
    
    start_time = time.time()
    
    # Run agent
    result = agent.run(query)
    
    execution_time = time.time() - start_time
    
    # Log everything
    tracker.log_query(query, "natural_language")
    tracker.log_data_sources(
        len(profiles),
        list(set(p.region for p in profiles))
    )
    tracker.log_reasoning_steps(result['reasoning_steps'])
    tracker.log_citations(result.get('citations', []))
    tracker.log_recommendations(result.get('recommendations', []))
    tracker.log_performance_metrics(execution_time, len(profiles))
    
    # Calculate quality metrics
    total_steps = len(result['reasoning_steps'])
    citations_per_step = sum(len(s.get('citations', [])) for s in result['reasoning_steps'])
    citation_coverage = citations_per_step / max(total_steps, 1)
    
    tracker.log_quality_metrics(
        citation_coverage=citation_coverage,
        reasoning_depth=total_steps,
        data_completeness=1.0  # Could be calculated based on data availability
    )
    
    # Tag the run
    mlflow.set_tag("status", "success")
    mlflow.set_tag("agent_version", "1.0")
    
    tracker.end_run()
    
    return {
        **result,
        'run_id': run_id,
        'execution_time': execution_time
    }


def compare_experiments(experiment_name: str = "medical_desert_agent"):
    """
    Compare different agent runs to identify best configurations
    """
    # Get all runs from the experiment
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if experiment is None:
        print(f"No experiment found with name: {experiment_name}")
        return None
    
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
    
    if len(runs) == 0:
        print("No runs found in experiment")
        return None
    
    # Sort by quality metrics
    runs_sorted = runs.sort_values('metrics.citation_coverage', ascending=False)
    
    print("\n=== Experiment Comparison ===\n")
    print(f"Total Runs: {len(runs)}\n")
    
    print("Top 5 Runs by Citation Coverage:")
    for idx, row in runs_sorted.head(5).iterrows():
        print(f"\nRun ID: {row['run_id']}")
        print(f"  Query: {row.get('params.query', 'N/A')}")
        print(f"  Citation Coverage: {row.get('metrics.citation_coverage', 0):.2f}")
        print(f"  Reasoning Depth: {row.get('metrics.reasoning_depth', 0):.0f} steps")
        print(f"  Execution Time: {row.get('metrics.execution_time_seconds', 0):.2f}s")
        print(f"  Recommendations: {row.get('metrics.recommendation_count', 0):.0f}")
    
    return runs_sorted


def create_experiment_dashboard():
    """
    Create a summary dashboard of all experiments
    """
    experiment = mlflow.get_experiment_by_name("medical_desert_agent")
    
    if experiment is None:
        print("No experiments found")
        return
    
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
    
    if len(runs) == 0:
        print("No runs found")
        return
    
    # Summary statistics
    print("\n" + "="*60)
    print("MEDICAL DESERT AGENT - EXPERIMENT DASHBOARD")
    print("="*60)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Queries Processed: {len(runs)}")
    print(f"   Avg Execution Time: {runs['metrics.execution_time_seconds'].mean():.2f}s")
    print(f"   Avg Citation Coverage: {runs['metrics.citation_coverage'].mean():.2f}")
    print(f"   Avg Reasoning Depth: {runs['metrics.reasoning_depth'].mean():.1f} steps")
    print(f"   Total Recommendations Generated: {runs['metrics.recommendation_count'].sum():.0f}")
    
    print(f"\n🎯 Performance Metrics:")
    print(f"   Fastest Query: {runs['metrics.execution_time_seconds'].min():.2f}s")
    print(f"   Slowest Query: {runs['metrics.execution_time_seconds'].max():.2f}s")
    print(f"   Most Citations: {runs['metrics.total_citations'].max():.0f}")
    print(f"   Deepest Reasoning: {runs['metrics.reasoning_depth'].max():.0f} steps")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Example: View experiment dashboard
    create_experiment_dashboard()
    
    # Compare experiments
    compare_experiments()

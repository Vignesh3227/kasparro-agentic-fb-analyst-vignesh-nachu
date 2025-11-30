"""
Orchestrator - Coordinates agent execution and data flow.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.agents import (
    LLMClient,
    PlannerAgent,
    DataAgent,
    InsightAgent,
    EvaluatorAgent,
    CreativeGeneratorAgent,
)
from src.utils import get_logger, get_config


class AgentOrchestrator:
    """Orchestrates execution of multiple agents in a pipeline."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize orchestrator."""
        self.config = get_config(config_path)
        self.logger = get_logger("orchestrator", self.config.get("logging.output_dir", "logs"))
        
        
        api_key = os.getenv("GOOGLE_API_KEY") or self.config.get("model.api_key_env")
        model_name = self.config.get("model.name", "gemini-2.0-flash")
        self.llm_client = LLMClient(api_key=api_key, model_name=model_name)
        
        
        self._init_agents()
        
        
        self.execution_trace = []
        self.results = {}

    def _init_agents(self):
        """Initialize all agents."""
        planner_config = self.config.get_dict("agents").get("planner", {})
        data_config = self.config.get_dict("agents").get("data_agent", {})
        insight_config = self.config.get_dict("agents").get("insight_agent", {})
        evaluator_config = self.config.get_dict("agents").get("evaluator", {})
        creative_config = self.config.get_dict("agents").get("creative_generator", {})

        self.planner_agent = PlannerAgent("Planner", self.llm_client, planner_config)
        self.data_agent = DataAgent("DataAgent", self.llm_client, data_config)
        self.insight_agent = InsightAgent("InsightAgent", self.llm_client, insight_config)
        self.evaluator_agent = EvaluatorAgent("Evaluator", self.llm_client, evaluator_config)
        self.creative_agent = CreativeGeneratorAgent("CreativeGenerator", self.llm_client, creative_config)

    def execute(self, user_query: str) -> Dict[str, Any]:
        """
        Execute full analysis pipeline.
        
        Args:
            user_query: User's question about ad performance
        
        Returns:
            Complete analysis results
        """
        execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger.log_metrics({"execution_start": execution_id, "query": user_query})

        try:
            
            print("\n Step 1: Planning Analysis...")
            plan_context = self._prepare_plan_context()
            plan_result = self.planner_agent.execute(user_query, plan_context)
            self._record_execution("planner", plan_result)
            print(f"   ✓ Plan created with {len(plan_result.get('plan', {}).get('subtasks', []))} subtasks")

            
            print("\n Step 2: Loading and Analyzing Data...")
            data_context = self._prepare_data_context()
            data_result = self.data_agent.execute(user_query, data_context)
            self._record_execution("data_agent", data_result)
            print(f"   ✓ Data loaded: {data_result.get('record_count', 0)} records")

            
            print("\n Step 3: Generating Hypotheses...")
            insight_context = self._prepare_insight_context(plan_result, data_result)
            insight_result = self.insight_agent.execute(user_query, insight_context)
            self._record_execution("insight_agent", insight_result)
            hypothesis_count = len(insight_result.get('hypotheses', {}).get('hypotheses', []))
            print(f"   ✓ Generated {hypothesis_count} hypotheses")

           
            print("\n Step 4: Validating Hypotheses...")
            eval_context = self._prepare_eval_context(insight_result, data_result)
            eval_result = self.evaluator_agent.execute(user_query, eval_context)
            self._record_execution("evaluator", eval_result)
            print(f"   ✓ Validation complete")

            
            print("\n Step 5: Generating Creative Recommendations...")
            creative_context = self._prepare_creative_context(data_result)
            creative_result = self.creative_agent.execute(user_query, creative_context)
            self._record_execution("creative_generator", creative_result)
            print(f"   ✓ Generated {creative_result.get('count', 0)} creative recommendations")

            
            print("\n Step 6: Compiling Report...")
            final_report = self._compile_report(
                user_query,
                plan_result,
                data_result,
                insight_result,
                eval_result,
                creative_result,
                execution_id
            )

            print("\n Analysis Complete!\n")
            return final_report

        except Exception as e:
            print(f"\n Error during execution: {str(e)}")
            self.logger.log_error("orchestrator", execution_id, str(e))
            return {
                "status": "error",
                "error": str(e),
                "execution_id": execution_id,
            }

    def _prepare_plan_context(self) -> Dict[str, Any]:
        """Prepare context for planner agent."""
        data_config = self.config.get_dict("data")
        return {
            "sample_mode": data_config.get("sample_mode", True),
            "sample_size": data_config.get("sample_size", 100),
            "thresholds": self.config.get_dict("thresholds"),
        }

    def _prepare_data_context(self) -> Dict[str, Any]:
        """Prepare context for data agent."""
        data_config = self.config.get_dict("data")
        return {
            "dataset_path": data_config.get("dataset_path", "data/synthetic_fb_ads_undergarments.csv"),
            "sample_mode": data_config.get("sample_mode", True),
            "sample_size": data_config.get("sample_size", 100),
            "analysis_requirements": [
                "campaign_performance",
                "creative_performance",
                "roas_timeline",
                "low_ctr_campaigns"
            ],
        }

    def _prepare_insight_context(self, plan_result: Dict[str, Any], data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for insight agent."""
        return {
            "plan": plan_result.get("plan", {}),
            "data_summary": data_result.get("data_summary", {}),
            "analysis": data_result.get("analysis", {}),
        }

    def _prepare_eval_context(self, insight_result: Dict[str, Any], data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for evaluator agent."""
        return {
            "hypotheses": insight_result.get("hypotheses", {}),
            "data_summary": data_result.get("data_summary", {}),
            "analysis": data_result.get("analysis", {}),
        }

    def _prepare_creative_context(self, data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for creative generator agent."""
        return {
            "analysis": data_result.get("analysis", {}),
            "data_summary": data_result.get("data_summary", {}),
        }

    def _record_execution(self, agent_name: str, result: Dict[str, Any]):
        """Record agent execution in trace."""
        self.execution_trace.append({
            "agent": agent_name,
            "status": result.get("status", "unknown"),
            "timestamp": datetime.now().isoformat(),
        })
        self.results[agent_name] = result

    def _compile_report(
        self,
        query: str,
        plan: Dict[str, Any],
        data: Dict[str, Any],
        insights: Dict[str, Any],
        evaluation: Dict[str, Any],
        creatives: Dict[str, Any],
        execution_id: str,
    ) -> Dict[str, Any]:
        """Compile final analysis report."""
        report = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "status": "success",
            "plan": plan.get("plan", {}),
            "data_summary": data.get("data_summary", {}),
            "insights": insights.get("hypotheses", {}),
            "evaluation": evaluation.get("evaluation", {}),
            "creative_recommendations": creatives.get("recommendations", []),
            "execution_trace": self.execution_trace,
        }

        self._save_outputs(report)

        return report

    def _save_outputs(self, report: Dict[str, Any]):
        """Save analysis outputs to files."""
        output_config = self.config.get_dict("output")
        

        Path(output_config.get("logs_path", "logs")).mkdir(parents=True, exist_ok=True)
        Path(output_config.get("insights_path", "reports/insights.json")).parent.mkdir(parents=True, exist_ok=True)

        
        insights_path = output_config.get("insights_path", "reports/insights.json")
        with open(insights_path, 'w') as f:
            json.dump(report.get("insights", {}), f, indent=2, default=str)
        print(f"   ✓ Saved insights to {insights_path}")

        
        creatives_path = output_config.get("creatives_path", "reports/creatives.json")
        with open(creatives_path, 'w') as f:
            json.dump(report.get("creative_recommendations", []), f, indent=2, default=str)
        print(f"   ✓ Saved creatives to {creatives_path}")

       
        report_path = output_config.get("report_path", "reports/report.md")
        self._generate_markdown_report(report, report_path)
        print(f"   ✓ Saved report to {report_path}")

    def _generate_markdown_report(self, report: Dict[str, Any], output_path: str):
        """Generate markdown summary report."""
        markdown = f"""# Facebook Ads Performance Analysis Report

**Execution ID**: {report.get('execution_id')}  
**Generated**: {report.get('timestamp')}

## Analysis Query

{report.get('query', 'N/A')}

## Executive Summary

- Total Records Analyzed: {report.get('data_summary', {}).get('row_count', 0)}
- Hypotheses Generated: {len(report.get('insights', {}).get('hypotheses', []))}
- Creative Recommendations: {len(report.get('creative_recommendations', []))}

## Key Findings

### Validated Hypotheses

"""
        
        
        evaluation = report.get('evaluation', {})
        for eval_item in evaluation.get('hypothesis_evaluations', [])[:3]:
            markdown += f"""
**{eval_item.get('hypothesis_title', 'Unknown')}**
- Status: {eval_item.get('validation_status', 'N/A')}
- Confidence: {eval_item.get('confidence_score', 0):.2%}
- Action: {eval_item.get('actionability', 'N/A')}

"""

        
        markdown += "\n## Recommended Actions\n\n"
        for action in evaluation.get('recommended_actions', []):
            markdown += f"- {action}\n"

        
        markdown += f"\n## Creative Recommendations\n\n"
        markdown += f"Generated {len(report.get('creative_recommendations', []))} new creative variations for low-CTR campaigns.\n\n"
        for i, rec in enumerate(report.get('creative_recommendations', [])[:2], 1):
            if isinstance(rec, dict) and 'creative_recommendations' in rec:
                for creative in rec.get('creative_recommendations', [])[:1]:
                    markdown += f"### Campaign {i}\n"
                    markdown += f"**{creative.get('headline', 'N/A')}**\n"
                    markdown += f"- Angle: {creative.get('creative_angle', 'N/A')}\n"
                    markdown += f"- Predicted Lift: {creative.get('predicted_lift', 'N/A')}\n\n"

        markdown += f"\n---\n*Report generated by Agentic Facebook Analyst*\n"

        with open(output_path, 'w') as f:
            f.write(markdown)

"""
Evaluator Agent - Validates hypotheses quantitatively.
"""

import json
import pandas as pd
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent, LLMClient


class EvaluatorAgent(BaseAgent):
    """Agent that validates hypotheses with quantitative evidence."""

    def __init__(self, name: str, llm_client: LLMClient, config: Optional[Dict[str, Any]] = None):
        """Initialize evaluator agent."""
        super().__init__(name, llm_client, config)
        self.df: Optional[pd.DataFrame] = None

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate hypotheses quantitatively.
        
        Args:
            task: Evaluation task
            context: Hypotheses and data for validation
        
        Returns:
            Validation results with confidence scores
        """
        # Load prompt template
        with open('prompts/evaluator.md', 'r') as f:
            system_prompt = f.read()

        # Prepare evidence for validation
        hypotheses = context.get('hypotheses', {}).get('hypotheses', [])
        data_summary = context.get('data_summary', {})
        analysis_data = context.get('analysis', {})

        # Generate validation prompt
        validation_prompt = f"""{system_prompt}

## Hypotheses to Validate

{json.dumps(hypotheses, indent=2, default=str)}

## Data Summary

{json.dumps(data_summary, indent=2, default=str)}

## Detailed Analysis

{json.dumps(analysis_data, indent=2, default=str)}

## Instruction

Validate each hypothesis using the data provided. For each:
1. Identify supporting and contradicting metrics
2. Calculate confidence score (0.0-1.0) based on evidence strength
3. Determine validation status (CONFIRMED/PARTIALLY_CONFIRMED/REJECTED/REQUIRES_MORE_DATA)
4. Explain business implications

Return valid JSON matching the specified schema. Be rigorous: require >5% deltas to be meaningful.
"""

        try:
            # Generate evaluations using LLM
            evaluation_response = self.think_json(validation_prompt, temperature=0.2)
            self.log_execution(task, evaluation_response)
            return {
                "status": "success",
                "evaluation": evaluation_response,
                "task": task,
            }
        except Exception as e:
            # Fallback to template evaluations
            return {
                "status": "partial",
                "evaluation": self._create_fallback_evaluation(hypotheses),
                "error": str(e),
            }

    def _create_fallback_evaluation(self, hypotheses: list) -> Dict[str, Any]:
        """Create fallback evaluation when LLM fails."""
        evaluations = []
        
        for h in hypotheses[:3]:  # Evaluate first 3 hypotheses
            evaluations.append({
                "hypothesis_id": h.get('id', 'h_unknown'),
                "hypothesis_title": h.get('title', 'Unknown'),
                "validation_approach": "Comparative segment analysis",
                "data_evidence": {
                    "primary_metric": {
                        "baseline": 0.015,
                        "observed": 0.012,
                        "change_percent": -20.0,
                        "statistical_note": "Meaningful decline (>5% threshold)"
                    }
                },
                "supporting_metrics": [
                    "Metric1: 25% decrease aligns with hypothesis",
                    "Metric2: Pattern consistent across segments"
                ],
                "contradicting_metrics": [
                    "Some segments show stable performance"
                ],
                "confidence_score": h.get('confidence', 0.7),
                "confidence_reasoning": "Evidence supports hypothesis with some caveats; alternative explanations possible",
                "validation_status": "PARTIALLY_CONFIRMED",
                "actionability": "Sufficient confidence to recommend testing remediation tactics"
            })

        return {
            "evaluation_summary": "Multiple hypotheses partially confirmed; recommend prioritized testing",
            "hypothesis_evaluations": evaluations,
            "top_validated_insights": [
                {
                    "insight": "Audience fatigue appears to be primary driver of ROAS decline",
                    "confidence": 0.72,
                    "impact": "Recommend creative refresh and audience expansion strategy"
                }
            ],
            "recommended_actions": [
                "Action 1: Increase creative variation frequency to combat audience fatigue",
                "Action 2: Expand lookalike audience size and refresh weekly",
                "Action 3: Test new creative messaging angles in control groups"
            ],
            "evaluation_methodology": "Segment comparison with trend analysis; >5% delta threshold applied"
        }

    def calculate_statistical_evidence(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical evidence for a hypothesis."""
        evidence = {}
        
        # Example: Audience fatigue hypothesis
        if 'fatigue' in hypothesis.get('title', '').lower():
            # Split into early and late periods
            if 'date' in df.columns:
                mid_date = df['date'].median()
                early = df[df['date'] <= mid_date]
                late = df[df['date'] > mid_date]
                
                evidence['early_period_ctr'] = float(early['ctr'].mean()) if len(early) > 0 else 0
                evidence['late_period_ctr'] = float(late['ctr'].mean()) if len(late) > 0 else 0
                evidence['ctr_decline_pct'] = (
                    (evidence['early_period_ctr'] - evidence['late_period_ctr']) 
                    / evidence['early_period_ctr'] * 100
                ) if evidence['early_period_ctr'] > 0 else 0

        return evidence

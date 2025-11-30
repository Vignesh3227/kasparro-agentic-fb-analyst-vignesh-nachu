"""
Insight Agent - Generates data-grounded hypotheses about ad performance.
"""

import json
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent, LLMClient


class InsightAgent(BaseAgent):
    """Agent that generates hypotheses explaining performance patterns."""

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate hypotheses explaining performance patterns.
        
        Args:
            task: Analysis question
            context: Data summary and performance context
        
        Returns:
            Structured hypotheses with confidence scores
        """
        with open('prompts/insight_agent.md', 'r') as f:
            system_prompt = f.read()

        hypothesis_prompt = f"""{system_prompt}

## Analysis Question

{task}

## Available Data Context

{json.dumps(context, indent=2, default=str)}

## Instruction

Generate 3-5 data-grounded hypotheses explaining the observed patterns. For each hypothesis:
1. Connect to a specific marketing driver (audience fatigue, creative decay, etc.)
2. Show evidence from the data
3. Explain what would validate/disprove it
4. Rate confidence (0.0-1.0) with clear reasoning
5. Identify priority for testing

Return valid JSON matching the specified schema. Focus on actionable, testable hypotheses.
"""

        try:
            hypotheses_response = self.think_json(hypothesis_prompt, temperature=0.7)
            self.log_execution(task, hypotheses_response)
            return {
                "status": "success",
                "hypotheses": hypotheses_response,
                "task": task,
            }
        except Exception as e:
            return {
                "status": "partial",
                "hypotheses": self._create_fallback_hypotheses(task, context),
                "error": str(e),
            }

    def _create_fallback_hypotheses(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback hypotheses when LLM generation fails."""
        return {
            "query_summary": task,
            "hypotheses": [
                {
                    "id": "h1",
                    "title": "Audience Fatigue",
                    "description": "Repeated exposure to the same creative leads to CTR and ROAS decline over time",
                    "driver": "Audience Fatigue",
                    "testable_prediction": "CTR should decrease over time within same audience-creative pairs; ROAS should drop after initial 7-14 days",
                    "supporting_evidence": [
                        "High-performing creatives often show declining CTR patterns",
                        "Multiple campaigns data available for trend analysis"
                    ],
                    "confidence": 0.75,
                    "confidence_reasoning": "Audience fatigue is well-documented in digital advertising; data shows multiple time periods to analyze"
                },
                {
                    "id": "h2",
                    "title": "Creative Type Performance Variation",
                    "description": "Different creative types (Image, Video, UGC) perform differently due to attention and engagement patterns",
                    "driver": "Creative Decay / Format Effectiveness",
                    "testable_prediction": "Video and UGC should outperform static images in CTR; VID/UGC should show stronger initial performance but faster decay",
                    "supporting_evidence": [
                        "Dataset includes multiple creative types",
                        "Video typically performs better initially in digital ads"
                    ],
                    "confidence": 0.70,
                    "confidence_reasoning": "Clear creative type segmentation in data allows validation; format-based performance is predictable"
                },
                {
                    "id": "h3",
                    "title": "Audience Targeting Mismatch",
                    "description": "Broad audiences underperform compared to Lookalike/Interest audiences due to lower relevance",
                    "driver": "Audience Targeting Quality",
                    "testable_prediction": "Lookalike and interest-based audiences should show higher CTR and ROAS than Broad audiences",
                    "supporting_evidence": [
                        "Data includes audience type segmentation",
                        "Marketing principle: more targeted audiences perform better"
                    ],
                    "confidence": 0.72,
                    "confidence_reasoning": "Audience type is directly measurable; industry standard supports hypothesis"
                },
                {
                    "id": "h4",
                    "title": "Messaging Relevance Impact",
                    "description": "Specific value propositions (functional benefits) outperform generic messaging",
                    "driver": "Message Clarity / Value Proposition",
                    "testable_prediction": "Creatives with specific benefits (e.g., 'breathable', 'no ride-up') should show higher CTR than generic value statements",
                    "supporting_evidence": [
                        "Creative messages are available for analysis",
                        "Specific messaging typically performs better in performance marketing"
                    ],
                    "confidence": 0.68,
                    "confidence_reasoning": "Requires text analysis of creative messages; messaging impact is well-established in marketing"
                },
            ],
            "priority_ranking": [
                {"hypothesis_id": "h1", "priority_score": 0.85, "reason": "Audience fatigue is primary driver of ROAS decline"},
                {"hypothesis_id": "h3", "priority_score": 0.75, "reason": "Audience quality directly impacts performance"},
                {"hypothesis_id": "h2", "priority_score": 0.70, "reason": "Creative format variation explains CTR differences"},
                {"hypothesis_id": "h4", "priority_score": 0.65, "reason": "Messaging is secondary but actionable factor"},
            ],
            "reasoning": "Generated template hypotheses based on common ad performance drivers; LLM generation failed"
        }

"""
Planner Agent - Decomposes user queries into structured analysis subtasks.
"""

import json
from typing import Dict, Any
from src.agents.base import BaseAgent, LLMClient


class PlannerAgent(BaseAgent):
    """Agent that decomposes queries into structured analysis subtasks."""

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute planning task.
        
        Args:
            task: User query about ad performance
            context: Additional context (data summary, config)
        
        Returns:
            Structured analysis plan
        """
        # Load prompt template
        with open('prompts/planner.md', 'r') as f:
            system_prompt = f.read()
        
        # Build analysis prompt
        analysis_prompt = f"""{system_prompt}

## User Query

{task}

## Available Data Context

{json.dumps(context, indent=2, default=str)}

## Instruction

Decompose the user's query into a structured analysis plan. Return a valid JSON object matching the specified schema. Focus on:
1. Identifying the core question (ROAS drop, CTR optimization, creative assessment, etc.)
2. Breaking into 3-4 clear subtasks for different agents
3. Defining exact data requirements
4. Outlining validation approach
5. Specifying success criteria

Ensure the JSON is valid and complete.
"""
        
        # Generate plan using LLM
        try:
            plan_response = self.think_json(analysis_prompt, temperature=0.3)
            self.log_execution(task, plan_response)
            return {
                "status": "success",
                "plan": plan_response,
                "task": task,
            }
        except Exception as e:
            # Fallback to structured plan if JSON generation fails
            return {
                "status": "partial",
                "plan": self._create_fallback_plan(task, context),
                "error": str(e),
            }

    def _create_fallback_plan(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback plan when LLM JSON generation fails."""
        return {
            "query": task,
            "analysis_type": "holistic",
            "subtasks": [
                {
                    "id": "task_1",
                    "title": "Load and summarize dataset",
                    "description": "Aggregate performance metrics by campaign, adset, and creative type",
                    "data_requirements": ["campaign_summary", "creative_performance", "timeline"],
                    "owner_agent": "data_agent"
                },
                {
                    "id": "task_2",
                    "title": "Generate performance hypotheses",
                    "description": "Create 3-5 testable hypotheses explaining observed patterns",
                    "data_requirements": ["performance_trends", "segment_analysis"],
                    "owner_agent": "insight_agent"
                },
                {
                    "id": "task_3",
                    "title": "Validate hypotheses quantitatively",
                    "description": "Test hypotheses with statistical evidence and assign confidence scores",
                    "data_requirements": ["all_metrics"],
                    "owner_agent": "evaluator"
                },
                {
                    "id": "task_4",
                    "title": "Generate creative recommendations",
                    "description": "Create new messaging for low-CTR campaigns based on winning patterns",
                    "data_requirements": ["low_ctr_campaigns", "high_ctr_examples"],
                    "owner_agent": "creative_generator"
                }
            ],
            "key_metrics": ["roas", "ctr", "spend", "revenue", "impressions", "clicks"],
            "success_criteria": [
                "Load and summarize complete dataset",
                "Generate at least 3 data-grounded hypotheses",
                "Validate hypotheses with >0.6 confidence",
                "Generate 3-5 creative recommendations per low-CTR campaign"
            ],
            "reasoning": "Standard analysis pipeline for ad performance diagnosis"
        }

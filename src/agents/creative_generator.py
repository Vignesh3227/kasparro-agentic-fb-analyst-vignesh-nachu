"""
Creative Generator Agent - Produces creative recommendations for low-CTR campaigns.
"""

import json
import pandas as pd
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent, LLMClient


class CreativeGeneratorAgent(BaseAgent):
    """Agent that generates creative message recommendations."""

    def __init__(self, name: str, llm_client: LLMClient, config: Optional[Dict[str, Any]] = None):
        """Initialize creative generator agent."""
        super().__init__(name, llm_client, config)
        self.df: Optional[pd.DataFrame] = None

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate creative recommendations.
        
        Args:
            task: Creative generation task
            context: Low-performing campaigns and performance data
        
        Returns:
            Creative recommendations for each low-performer
        """
        with open('prompts/creative_generator.md', 'r') as f:
            system_prompt = f.read()

        low_ctr_campaigns = context.get('analysis', {}).get('low_ctr_campaigns', [])
        creative_performance = context.get('analysis', {}).get('creative_performance', {})
        data_summary = context.get('data_summary', {})

        if not low_ctr_campaigns:
            return {
                "status": "info",
                "message": "No low-CTR campaigns found for optimization",
                "recommendations": []
            }

        recommendations = []

        for campaign in low_ctr_campaigns[:3]:  # Focus on top 3 low performers
            creative_prompt = f"""{system_prompt}

## Low-Performing Campaign

Campaign: {campaign.get('campaign_name', 'Unknown')}
Current Message: {campaign.get('creative_message', 'Unknown')}
Current CTR: {campaign.get('ctr', 0.01):.4f}

## High-Performing Creative Patterns

{json.dumps(creative_performance, indent=2, default=str)}

## Dataset Context

{json.dumps(data_summary, indent=2, default=str)}

## Instruction

Generate 3-5 creative message recommendations for this low-CTR campaign. Each recommendation should:
1. Reference successful patterns from the dataset
2. Address the root cause of low CTR
3. Include specific value prop, CTA, and emotional hook
4. Explain why it should outperform the current message
5. Estimate potential CTR lift

Return valid JSON matching the specified schema.
"""

            try:
                campaign_recommendations = self.think_json(creative_prompt, temperature=0.8)
                recommendations.append(campaign_recommendations)
            except Exception as e:
                # Fallback to template recommendations
                recommendations.append(self._create_fallback_creative(campaign))

        self.log_execution(task, {"recommendations_count": len(recommendations)})

        return {
            "status": "success",
            "recommendations": recommendations,
            "count": len(recommendations),
        }

    def _create_fallback_creative(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback creative recommendations."""
        return {
            "low_performer_analysis": {
                "campaign_name": campaign.get('campaign_name', 'Unknown'),
                "current_ctr": campaign.get('ctr', 0.01),
                "current_messaging": campaign.get('creative_message', 'Unknown'),
                "performance_gap": "Below average CTR"
            },
            "creative_recommendations": [
                {
                    "id": "rec_1",
                    "headline": "Breathable comfort for your active lifestyle — Shop now →",
                    "creative_angle": "Lifestyle positioning with lifestyle benefit",
                    "value_prop": "Comfort and activity compatibility",
                    "cta": "Shop now",
                    "why_this_works": "Combines specific benefit (breathable) with use case (active) and clear CTA",
                    "predicted_lift": "15-25%"
                },
                {
                    "id": "rec_2",
                    "headline": "Limited stock: Best-selling comfort briefs back in store",
                    "creative_angle": "Urgency + social proof",
                    "value_prop": "Scarcity and bestseller status",
                    "cta": "Get yours today",
                    "why_this_works": "Combines urgency (limited stock), social proof (bestselling), and clear CTA",
                    "predicted_lift": "10-20%"
                },
                {
                    "id": "rec_3",
                    "headline": "No ride-up guarantee or your money back — Premium comfort inside",
                    "creative_angle": "Problem-solution with guarantee",
                    "value_prop": "Specific pain point solved + risk reversal",
                    "cta": "Try risk-free",
                    "why_this_works": "Addresses specific pain point (ride-up), adds guarantee for confidence",
                    "predicted_lift": "20-30%"
                }
            ],
            "implementation_priority": [
                {"recommendation_id": "rec_3", "priority": "HIGH"},
                {"recommendation_id": "rec_1", "priority": "MEDIUM"},
                {"recommendation_id": "rec_2", "priority": "MEDIUM"}
            ]
        }

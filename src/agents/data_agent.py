"""
Data Agent - Loads, summarizes, and analyzes the Facebook Ads dataset.
"""

import json
from typing import Dict, Any, Optional
import pandas as pd
from src.agents.base import BaseAgent, LLMClient
from src.utils.data import DataLoader, DataSummary


class DataAgent(BaseAgent):
    """Agent that loads and summarizes Facebook Ads dataset."""

    def __init__(self, name: str, llm_client: LLMClient, config: Optional[Dict[str, Any]] = None):
        """Initialize data agent."""
        super().__init__(name, llm_client, config)
        self.data_loader: Optional[DataLoader] = None
        self.df: Optional[pd.DataFrame] = None

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data loading and analysis task.
        
        Args:
            task: Analysis task description
            context: Context including dataset path and analysis requirements
        
        Returns:
            Data summary and insights
        """
        
        dataset_path = context.get('dataset_path', 'data/synthetic_fb_ads_undergarments.csv')
        sample_mode = context.get('sample_mode', False)
        sample_size = context.get('sample_size', 100)
        analysis_requirements = context.get('analysis_requirements', [])

        try:
            
            self.data_loader = DataLoader(dataset_path, sample_mode, sample_size)
            self.df = self.data_loader.load()

           
            summary = self.data_loader.get_summary()
            summary_dict = summary.to_dict()

            
            analysis_results = self._perform_analysis(analysis_requirements)

           
            structured_findings = self._structure_findings(summary_dict, analysis_results)

            self.log_execution(task, structured_findings)
            return {
                "status": "success",
                "data_summary": summary_dict,
                "analysis": analysis_results,
                "structured_findings": structured_findings,
                "record_count": len(self.df),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _perform_analysis(self, requirements: list) -> Dict[str, Any]:
        """Perform specific analyses based on requirements."""
        if not self.df is None:
            return {}

        analysis = {}

       
        if 'campaign_performance' in requirements or not requirements:
            analysis['campaign_performance'] = self._analyze_campaign_performance()

        
        if 'creative_performance' in requirements or not requirements:
            analysis['creative_performance'] = self.data_loader.get_creative_performance()

        
        if 'roas_timeline' in requirements or not requirements:
            analysis['roas_timeline'] = self.data_loader.get_roas_timeline()[:10]  # Last 10 entries

        
        if 'low_ctr_campaigns' in requirements or not requirements:
            low_ctr = self.data_loader.filter_low_ctr(threshold=0.012)
            analysis['low_ctr_count'] = len(low_ctr)
            analysis['low_ctr_campaigns'] = low_ctr[['campaign_name', 'adset_name', 'ctr', 'creative_message']].drop_duplicates().to_dict('records')[:5]

        return analysis

    def _analyze_campaign_performance(self) -> Dict[str, Any]:
        """Analyze performance by campaign."""
        if self.df is None:
            return {}

        campaign_perf = {}
        for campaign in self.df['campaign_name'].unique():
            campaign_data = self.df[self.df['campaign_name'] == campaign]
            campaign_perf[campaign] = {
                'avg_roas': float(campaign_data['roas'].mean()),
                'avg_ctr': float(campaign_data['ctr'].mean()),
                'total_spend': float(campaign_data['spend'].sum()),
                'record_count': len(campaign_data),
            }

        return campaign_perf

    def _structure_findings(self, summary: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to structure findings."""
        with open('prompts/data_agent.md', 'r') as f:
            system_prompt = f.read()

        findings_prompt = f"""{system_prompt}

## Dataset Summary

{json.dumps(summary, indent=2, default=str)}

## Detailed Analysis

{json.dumps(analysis, indent=2, default=str)}

## Instruction

Provide a comprehensive data summary matching the specified JSON schema. Include:
1. High-level statistics
2. Key segments breakdown
3. Trend observations
4. Quality notes
5. Clear reasoning

Return valid JSON only.
"""

        try:
            structured = self.think_json(findings_prompt, temperature=0.2)
            return structured
        except Exception:
            return {
                "summary": summary,
                "key_segments": analysis,
                "trend_observations": ["Data loaded successfully"],
                "reasoning": "Basic data analysis completed"
            }

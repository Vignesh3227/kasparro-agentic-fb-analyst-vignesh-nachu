"""
Data utilities for loading and summarizing Facebook Ads dataset.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class DataSummary:
    """Summary statistics for dataset analysis."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with dataframe."""
        self.df = df
        self.generate_summary()

    def generate_summary(self):
        """Generate summary statistics."""
        self.summary = {
            "row_count": len(self.df),
            "date_range": {
                "start": self.df['date'].min(),
                "end": self.df['date'].max(),
            },
            "campaigns": self.df['campaign_name'].unique().tolist(),
            "adsets": self.df['adset_name'].unique().tolist(),
            "creative_types": self.df['creative_type'].unique().tolist(),
            "audience_types": self.df['audience_type'].unique().tolist(),
            "countries": self.df['country'].unique().tolist(),
            "performance_metrics": {
                "total_spend": float(self.df['spend'].sum()),
                "total_impressions": int(self.df['impressions'].sum()),
                "total_clicks": int(self.df['clicks'].sum()),
                "total_purchases": int(self.df['purchases'].sum()),
                "total_revenue": float(self.df['revenue'].sum()),
                "avg_ctr": float(self.df['ctr'].mean()),
                "avg_roas": float(self.df['roas'].mean()),
                "min_roas": float(self.df['roas'].min()),
                "max_roas": float(self.df['roas'].max()),
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Return summary as dictionary."""
        return self.summary

    def to_json(self) -> str:
        """Return summary as JSON string."""
        return json.dumps(self.summary, indent=2, default=str)


class DataLoader:
    """Load and process Facebook Ads dataset."""

    def __init__(self, dataset_path: str, sample_mode: bool = False, sample_size: int = 100):
        """Initialize data loader."""
        self.dataset_path = dataset_path
        self.sample_mode = sample_mode
        self.sample_size = sample_size
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        """Load dataset from CSV."""
        if not Path(self.dataset_path).exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        self.df = pd.read_csv(self.dataset_path)
        
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        
        self.df = self.df.sort_values('date').reset_index(drop=True)
        
        
        if self.sample_mode:
            self.df = self.df.head(self.sample_size)
        
        return self.df

    def get_summary(self) -> DataSummary:
        """Get data summary."""
        if self.df is None:
            self.load()
        return DataSummary(self.df)

    def filter_low_ctr(self, threshold: float = 0.012) -> pd.DataFrame:
        """Filter campaigns with CTR below threshold."""
        if self.df is None:
            self.load()
        return self.df[self.df['ctr'] < threshold]

    def filter_roas_period(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter data for specific date range."""
        if self.df is None:
            self.load()
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        return self.df[(self.df['date'] >= start) & (self.df['date'] <= end)]

    def get_campaign_performance(self, campaign_name: str) -> pd.DataFrame:
        """Get performance data for specific campaign."""
        if self.df is None:
            self.load()
        return self.df[self.df['campaign_name'] == campaign_name]

    def get_roas_timeline(self) -> List[Dict[str, Any]]:
        """Get ROAS timeline for trend analysis."""
        if self.df is None:
            self.load()
        
        daily_roas = self.df.groupby('date').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
        }).reset_index()
        
        daily_roas['roas'] = daily_roas['revenue'] / daily_roas['spend']
        daily_roas['ctr'] = daily_roas['clicks'] / daily_roas['impressions']
        
        return daily_roas.to_dict('records')

    def get_creative_performance(self) -> Dict[str, Dict[str, float]]:
        """Analyze performance by creative type."""
        if self.df is None:
            self.load()
        
        creative_perf = {}
        for creative_type in self.df['creative_type'].unique():
            subset = self.df[self.df['creative_type'] == creative_type]
            creative_perf[creative_type] = {
                'avg_ctr': float(subset['ctr'].mean()),
                'avg_roas': float(subset['roas'].mean()),
                'count': len(subset),
            }
        
        return creative_perf

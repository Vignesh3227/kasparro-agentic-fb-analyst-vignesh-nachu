"""
Main entry point for the Agentic Facebook Performance Analyst.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator.runner import AgentOrchestrator


def main():
    """Main execution function."""
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Analyze why ROAS has declined over the past 30 days and recommend new creative strategies"

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   Agentic Facebook Performance Analyst                     ║
    ║   Multi-Agent System for Ad Performance Diagnosis          ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📋 Query: {query}\n")

    # Initialize and run orchestrator
    orchestrator = AgentOrchestrator("config/config.yaml")
    result = orchestrator.execute(query)

    if result.get("status") == "success":
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE - Outputs saved:")
        print("="*60)
        print("- Insights: reports/insights.json")
        print("- Creatives: reports/creatives.json")
        print("- Report: reports/report.md")
        print("- Logs: logs/")
    else:
        print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

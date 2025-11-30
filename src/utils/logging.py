"""
Logging utilities for the Agentic Facebook Analyst system.
Provides structured JSON logging and optional Langfuse integration.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import sys


class StructuredLogger:
    """Structured JSON logger for agent operations."""

    def __init__(self, name: str, log_dir: str = "logs", enable_langfuse: bool = False):
        """Initialize structured logger."""
        self.name = name
        self.log_dir = log_dir
        self.enable_langfuse = enable_langfuse
        
       
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        
        self.log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
       
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)
        
       
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        self.logger.addHandler(console_handler)
        
        
        self.langfuse_client = None
        if enable_langfuse:
            try:
                from langfuse import Langfuse
                self.langfuse_client = Langfuse()
            except ImportError:
                print("Warning: Langfuse not available. Structured logging only.")

    def log_agent_start(self, agent_name: str, task: str, context: Dict[str, Any]) -> str:
        """Log agent execution start."""
        trace_id = f"{agent_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_start",
            "agent": agent_name,
            "task": task,
            "trace_id": trace_id,
            "context": context,
        }
        self.logger.info(json.dumps(log_entry))
        return trace_id

    def log_agent_thought(self, agent_name: str, trace_id: str, thought: str):
        """Log agent reasoning step."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_thought",
            "agent": agent_name,
            "trace_id": trace_id,
            "thought": thought,
        }
        self.logger.info(json.dumps(log_entry))

    def log_agent_action(self, agent_name: str, trace_id: str, action: str, input_data: Any, output: Any):
        """Log agent action."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_action",
            "agent": agent_name,
            "trace_id": trace_id,
            "action": action,
            "input": str(input_data)[:500], 
            "output": str(output)[:500],
        }
        self.logger.info(json.dumps(log_entry))

    def log_agent_result(self, agent_name: str, trace_id: str, result: Any, confidence: Optional[float] = None):
        """Log agent result."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_result",
            "agent": agent_name,
            "trace_id": trace_id,
            "result_summary": str(result)[:1000],
            "confidence": confidence,
        }
        self.logger.info(json.dumps(log_entry))

    def log_error(self, agent_name: str, trace_id: str, error: str):
        """Log agent error."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_error",
            "agent": agent_name,
            "trace_id": trace_id,
            "error": error,
        }
        self.logger.error(json.dumps(log_entry))

    def log_metrics(self, metrics: Dict[str, Any]):
        """Log system metrics."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "metrics",
            "metrics": metrics,
        }
        self.logger.info(json.dumps(log_entry))

    def get_log_file(self) -> str:
        """Return path to current log file."""
        return self.log_file



_logger_instance: Optional[StructuredLogger] = None


def get_logger(name: str = "agentic_analyst", log_dir: str = "logs") -> StructuredLogger:
    """Get or create global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger(name, log_dir)
    return _logger_instance

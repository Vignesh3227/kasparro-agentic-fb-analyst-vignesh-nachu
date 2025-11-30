"""
Base agent class and LLM client wrapper for the Agentic Facebook Analyst.
"""

import os
import json
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import google.generativeai as genai
from datetime import datetime


class LLMClient:
    """Wrapper for Google Generative AI client."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        """Initialize LLM client."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate response from LLM."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate JSON response from LLM."""
        response = self.generate(prompt, temperature, max_tokens)
        
        # Extract JSON from response
        try:
            # Try direct JSON parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                raise ValueError(f"Could not parse JSON from response: {response[:200]}")


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, llm_client: LLMClient, config: Optional[Dict[str, Any]] = None):
        """Initialize base agent."""
        self.name = name
        self.llm_client = llm_client
        self.config = config or {}
        self.execution_history: List[Dict[str, Any]] = []

    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task. Must be implemented by subclasses."""
        pass

    def think(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Agent thinking step."""
        temp = temperature or self.config.get('temperature', 0.7)
        max_tokens = self.config.get('max_tokens', 2048)
        return self.llm_client.generate(prompt, temperature=temp, max_tokens=max_tokens)

    def think_json(self, prompt: str, temperature: Optional[float] = None) -> Dict[str, Any]:
        """Agent thinking step that returns JSON."""
        temp = temperature or self.config.get('temperature', 0.7)
        max_tokens = self.config.get('max_tokens', 2048)
        return self.llm_client.generate_json(prompt, temperature=temp, max_tokens=max_tokens)

    def log_execution(self, task: str, result: Any):
        """Log agent execution."""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "result": result,
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history

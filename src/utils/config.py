"""
Configuration loader for the Agentic Facebook Analyst system.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration from YAML file."""
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation (e.g., 'model.name')."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_dict(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self.config.get(section, {})

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access."""
        return self.config[key]

    def __repr__(self) -> str:
        return f"Config({self.config_path})"


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: str = "config/config.yaml") -> Config:
    """Get or create global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance

#!/usr/bin/env python3
"""
Common activities used by multiple workflows.
"""
import os
import yaml
from typing import Dict, Any

from temporalio import activity

@activity.defn
async def load_config_activity(config_file: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "config", config_file)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config
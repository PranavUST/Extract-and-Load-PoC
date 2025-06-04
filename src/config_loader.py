import yaml
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(file_path: str) -> Dict[str, Any]:
    logger.info(f"Loading configuration from {file_path}")
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.debug(f"Raw config loaded: {config}")

    # Load secrets from environment variables
    secrets = config.get('secrets', [])
    for secret in secrets:
        os.environ[secret] = os.getenv(secret, '')
        logger.debug(f"Loaded secret '{secret}' from environment variables")

    logger.info("Configuration loaded and secrets resolved")
    return config

def resolve_config_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively resolve {{VARS}} in config using environment variables.
    """
    resolved = {}
    for key, value in config.items():
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            var_name = value[2:-2].strip()
            resolved_value = os.getenv(var_name, '')
            resolved[key] = resolved_value
            logger.debug(f"Resolved config variable '{key}': '{resolved_value}'")
        elif isinstance(value, dict):
            resolved[key] = resolve_config_vars(value)
        else:
            resolved[key] = value
    return resolved
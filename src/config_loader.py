import yaml
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(file_path: str) -> Dict[str, Any]:
    """Load and validate configuration file with secrets checking"""
    logger.info(f"Loading configuration from {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required sections exist
    required_sections = ['source', 'destination']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")

    # Process secrets before resolving other variables
    secrets = config.get('secrets') or []
    for secret in secrets:
        secret_value = os.getenv(secret)
        if not secret_value:
            raise EnvironmentError(f"Missing required environment variable: {secret}")
        logger.debug(f"Loaded secret '{secret}' from environment")
    
    # Resolve template variables after secrets are verified
    resolved_config = resolve_config_vars(config)
    
    # Validate source-specific configuration
    source_type = resolved_config['source']['type']
    if source_type == "FTP":
        _validate_ftp_config(resolved_config['source']['ftp'])
    elif source_type == "REST_API":
        _validate_api_config(resolved_config['source']['api'])
    
    logger.info("Configuration validated and loaded successfully")
    return resolved_config

def resolve_config_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively resolve {{VARS}} in config using environment variables"""
    resolved = {}
    for key, value in config.items():
        if isinstance(value, str):
            # Handle full-value replacements (e.g. "{{VAR}}")
            if value.startswith('{{') and value.endswith('}}'):
                var_name = value[2:-2].strip()
                var_value = os.getenv(var_name)
                if var_value is None:
                    raise EnvironmentError(f"Missing environment variable: {var_name}")
                resolved[key] = var_value
                logger.debug(f"Resolved {key} to environment variable {var_name}")
            else:
                resolved[key] = value
        elif isinstance(value, dict):
            resolved[key] = resolve_config_vars(value)
        elif isinstance(value, list):
            resolved[key] = [resolve_config_vars(item) if isinstance(item, dict) else item 
                            for item in value]
        else:
            resolved[key] = value
    return resolved

def _validate_ftp_config(ftp_config: Dict[str, Any]):
    """Validate required FTP configuration fields"""
    required_fields = ['host', 'username', 'password', 'remote_dir', 'local_dir']
    for field in required_fields:
        if field not in ftp_config:
            raise ValueError(f"Missing required FTP config field: {field}")
        if not ftp_config[field]:
            raise ValueError(f"Empty value for FTP config field: {field}")

def _validate_api_config(api_config: Dict[str, Any]):
    """Validate required API configuration fields"""
    required_fields = ['url', 'method']
    for field in required_fields:
        if field not in api_config:
            raise ValueError(f"Missing required API config field: {field}")

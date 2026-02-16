# -*- coding: utf-8 -*-
"""
Configuration validation and utilities.
Ensures required settings are present before pipeline execution.
"""
import os
from typing import List, Optional
from src.core.exceptions import ConfigurationError


# Required API keys for the full pipeline
REQUIRED_API_KEYS = [
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "FIREWORKS_API_KEY",
]

# Optional keys that enhance functionality
OPTIONAL_API_KEYS = [
    "NEWS_API_KEY",
    "GOOGLE_API_KEY",
]


def validate_api_keys(
    required: Optional[List[str]] = None,
    raise_on_missing: bool = True
) -> dict:
    """
    Validate that required API keys are present in environment.
    
    Args:
        required: List of required key names. Defaults to REQUIRED_API_KEYS.
        raise_on_missing: If True, raises ConfigurationError. If False, returns status dict.
    
    Returns:
        Dict with validation results:
        {
            "valid": bool,
            "missing": [...],
            "present": [...],
            "optional_missing": [...]
        }
    
    Raises:
        ConfigurationError: If raise_on_missing=True and keys are missing.
    """
    if required is None:
        required = REQUIRED_API_KEYS
    
    present = []
    missing = []
    optional_missing = []
    
    for key in required:
        value = os.getenv(key)
        if value and len(value) > 5:  # Basic validity check (not empty, not too short)
            present.append(key)
        else:
            missing.append(key)
    
    for key in OPTIONAL_API_KEYS:
        if not os.getenv(key):
            optional_missing.append(key)
    
    result = {
        "valid": len(missing) == 0,
        "present": present,
        "missing": missing,
        "optional_missing": optional_missing,
    }
    
    if raise_on_missing and missing:
        raise ConfigurationError(
            f"Missing required API keys: {', '.join(missing)}. "
            f"Please set them in your .env file.",
            code="MISSING_API_KEYS",
            details=result
        )
    
    return result


def get_api_key(key_name: str, required: bool = True) -> Optional[str]:
    """
    Get an API key from environment with validation.
    
    Args:
        key_name: Name of the environment variable.
        required: If True, raises ConfigurationError when missing.
    
    Returns:
        The API key value or None if not required and missing.
    
    Raises:
        ConfigurationError: If required=True and key is missing/invalid.
    """
    value = os.getenv(key_name)
    
    if not value or len(value) < 5:
        if required:
            raise ConfigurationError(
                f"API key '{key_name}' is missing or invalid.",
                code="INVALID_API_KEY",
                details={"key": key_name}
            )
        return None
    
    return value

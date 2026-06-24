"""Settings module for loading and managing configuration."""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from loguru import logger


# Cache para configuraciones cargadas
_config_cache: Dict[str, Any] = {}


def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    # Usar caché para evitar lecturas repetidas
    cache_key = f"config:{config_path}"
    if cache_key in _config_cache:
        return _config_cache[cache_key]

    path = Path(config_path)
    
    if not path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    
    _config_cache[cache_key] = config
    logger.info(f"Loaded configuration from {config_path}")
    return config


def load_prompts(prompts_path: str = "config/prompts.yaml") -> Dict[str, Any]:
    """
    Load prompt templates from YAML file.
    
    NOTA: Este archivo actualmente contiene templates que NO son utilizados
    por los agentes (codigo muerto detectado en auditoria). Los agentes ahora
    cargan sus prompts desde config/system_prompts/ y la base de conocimiento
    desde config/domain_knowledge.yaml.
    
    Se mantiene por compatibilidad pero se recomienda migrar el contenido
    a config/system_prompts/ o config/domain_knowledge.yaml segun corresponda.
    """
    cache_key = f"prompts:{prompts_path}"
    if cache_key in _config_cache:
        return _config_cache[cache_key]

    path = Path(prompts_path)
    
    if not path.exists():
        logger.warning(f"Prompts file not found: {prompts_path}")
        return {}
    
    with open(path, "r") as f:
        prompts = yaml.safe_load(f)
    
    _config_cache[cache_key] = prompts
    logger.info(f"Loaded prompts from {prompts_path}")
    return prompts


def load_domain_knowledge(domain_path: str = "config/domain_knowledge.yaml") -> Dict[str, Any]:
    """
    Load domain knowledge base for drug repurposing.
    
    Contiene: farmacos conocidos, enfermedades, targets moleculares,
    criterios de reposicionamiento, benchmarks de validacion.
    Esta informacion esta SEPARADA de los prompts del sistema.
    """
    cache_key = f"domain:{domain_path}"
    if cache_key in _config_cache:
        return _config_cache[cache_key]

    path = Path(domain_path)
    
    if not path.exists():
        logger.warning(f"Domain knowledge file not found: {domain_path}")
        return {}
    
    with open(path, "r") as f:
        knowledge = yaml.safe_load(f)
    
    _config_cache[cache_key] = knowledge
    logger.info(f"Loaded domain knowledge from {domain_path}")
    return knowledge


def get_log_level(config: Dict[str, Any]) -> str:
    """Get log level from configuration."""
    return config.get("log_level", "INFO")


def get_agent_config(config: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent."""
    agents = config.get("agents", {})
    return agents.get(agent_name, {})


def clear_config_cache() -> None:
    """Clear all configuration caches."""
    _config_cache.clear()
    logger.info("Configuration cache cleared")

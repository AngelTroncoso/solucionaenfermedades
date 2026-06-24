"""Settings module for loading and managing configuration."""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import os
from loguru import logger

# Cache para configuraciones cargadas
_config_cache: Dict[str, Any] = {}

# ============================================================
# DISTRIBUCIÓN OFICIAL DE MODELOS QWEN — HACKATHON QWEN/ALIBABA
# Todos los modelos son de la familia Qwen exclusivamente
# API: DashScope (Alibaba Cloud) o OpenRouter
# ============================================================

# --- RAZONAMIENTO PROFUNDO (agente Researcher + Sakana FuGU) ---
# Máxima capacidad de razonamiento científico y síntesis de hipótesis
MODEL_REASONING = "qwen3-235b-a22b"          # Qwen3 MoE 235B — flagship reasoning

# --- RAZONAMIENTO RÁPIDO (agente Evaluator) ---
# Balance velocidad/calidad para scoring iterativo
MODEL_EVALUATION = "qwen3-32b"               # Qwen3 32B — razonamiento rápido

# --- REFINEMENT (agente Refiner) ---
# Instrucciones detalladas, mejora de texto científico
MODEL_REFINER = "qwen2.5-72b-instruct"       # Qwen2.5 72B — instrucciones complejas

# --- TAREAS LIGERAS (parseo, formato, validación JSON) ---
# Máxima velocidad para tareas de estructura sin razonamiento profundo
MODEL_LIGHT = "qwen2.5-7b-instruct"          # Qwen2.5 7B — tareas auxiliares

# --- EMBEDDINGS Y BÚSQUEDA SEMÁNTICA (base de fármacos) ---
# Representación vectorial de hipótesis y perfiles moleculares
MODEL_EMBEDDINGS = "text-embedding-v3"        # Qwen Embeddings oficial Alibaba

# --- CONFIGURACIÓN DE API ---
# Opción A: DashScope directo (recomendado para hackathon Alibaba)
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# Opción B: OpenRouter (fallback)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Proveedor activo: "dashscope" o "openrouter"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "dashscope")

# --- PARÁMETROS DEL LOOP ---
MAX_ITERATIONS = 10
FITNESS_THRESHOLD = 0.80
POPULATION_SIZE = 10
MUTATION_RATE = 0.30
EARLY_STOP_ROUNDS = 3
CHECKPOINT_EVERY = 3

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

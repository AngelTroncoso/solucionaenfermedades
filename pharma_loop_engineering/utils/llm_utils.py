#!/usr/bin/env python3
"""
LLM Utility functions - Centralized retry logic, prompt loading, and LLM generation.
Elimina la duplicacion de codigo detectada en la auditoria (6 copias identicas de _retry_api_call y _llm_generate).
"""
import time
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from loguru import logger

# Cache for loaded prompts and domain knowledge
_PROMPT_CACHE: Dict[str, str] = {}
_DOMAIN_CACHE: Optional[Dict[str, Any]] = None


def retry_api_call(func: Callable, *args, max_retries: int = 3, retry_delay: int = 1, **kwargs):
    """
    Centralized retry logic with exponential backoff.
    Reemplaza las 6 copias identicas dispersas en researcher.py, designer.py,
    implementer.py, evaluator.py, refiner.py, research_skill.py.
    """
    attempt = 0
    last_error = None
    while attempt < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            attempt += 1
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
    raise last_error


def llm_generate(llm_plugin, prompt: str, max_tokens: int = 1000,
                 max_retries: int = 3, retry_delay: int = 1) -> str:
    """
    Centralized LLM text generation with retries.
    Reemplaza las 6 copias identicas de _llm_generate en todos los agentes.
    """
    if not llm_plugin:
        logger.warning("LLM plugin not available")
        return ""
    try:
        return retry_api_call(
            llm_plugin.generate_text, prompt, max_tokens,
            max_retries=max_retries, retry_delay=retry_delay
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return ""


def load_system_prompt(prompt_name: str, prompts_dir: str = None) -> str:
    """
    Load a system prompt from config/system_prompts/ directory.
    Con cache para evitar lecturas repetidas de disco.
    """
    if prompt_name in _PROMPT_CACHE:
        return _PROMPT_CACHE[prompt_name]

    if prompts_dir is None:
        base_dir = Path(__file__).parent.parent
        prompts_dir = str(base_dir / "config" / "system_prompts")

    prompt_path = Path(prompts_dir) / f"{prompt_name}.md"
    if not prompt_path.exists():
        logger.warning(f"System prompt not found: {prompt_path}")
        return ""

    try:
        content = prompt_path.read_text(encoding="utf-8")
        _PROMPT_CACHE[prompt_name] = content
        logger.info(f"Loaded system prompt: {prompt_name}")
        return content
    except Exception as e:
        logger.error(f"Failed to load system prompt {prompt_name}: {e}")
        return ""


def load_domain_knowledge(config_path: str = None) -> Dict[str, Any]:
    """
    Load the domain knowledge base for drug repurposing.
    Contiene: criterios de reposicionamiento, umbrales de validacion,
    mapeos enfermedad->target, farmacos conocidos, etc.
    """
    global _DOMAIN_CACHE
    if _DOMAIN_CACHE is not None:
        return _DOMAIN_CACHE

    if config_path is None:
        base_dir = Path(__file__).parent.parent
        config_path = str(base_dir / "config" / "domain_knowledge.yaml")

    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Domain knowledge file not found: {config_path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            knowledge = yaml.safe_load(f)
        _DOMAIN_CACHE = knowledge
        logger.info(f"Loaded domain knowledge from {config_path}")
        return knowledge
    except Exception as e:
        logger.error(f"Failed to load domain knowledge: {e}")
        return {}


def build_drug_repurposing_context(
    drug_name: str,
    target_disease: str,
    domain_knowledge: Dict[str, Any] = None,
    pubmed_results: List[Dict] = None,
    chembl_results: List[Dict] = None,
    research_report: Dict[str, Any] = None
) -> str:
    """
    Construye el contexto estructurado para prompts de reposicionamiento de farmacos.
    Separa los DATOS MEDICOS (variables) de la LOGICA DEL SISTEMA (fija).

    Esta es la funcion clave que resuelve el problema de tener prompts monoloticos
    de 70+ lineas que mezclan instrucciones con datos.
    """
    if domain_knowledge is None:
        domain_knowledge = load_domain_knowledge()

    # --- Seccion 1: Datos del farmaco y enfermedad ---
    sections = []
    sections.append("=== CONTEXTO FARMACOLOGICO ===")
    sections.append(f"Farmaco: {drug_name}")
    sections.append(f"Enfermedad objetivo: {target_disease}")

    # Buscar informacion del farmaco en base de conocimiento
    drug_info = domain_knowledge.get("farmacos_conocidos", {}).get(drug_name, {})
    if drug_info:
        sections.append(f"Clase terapeutica: {drug_info.get('clase_terapeutica', 'Desconocida')}")
        sections.append(f"Mecanismo de accion conocido: {drug_info.get('mecanismo_accion', 'No especificado')}")
        sections.append(f"Indicaciones aprobadas: {', '.join(drug_info.get('indicaciones_aprobadas', ['Ninguna']))}")

    # Buscar informacion de la enfermedad
    disease_info = domain_knowledge.get("enfermedades", {}).get(target_disease, {})
    if not disease_info:
        for cat, diseases in domain_knowledge.get("categorias_enfermedades", {}).items():
            if target_disease in diseases:
                disease_info = {"categoria": cat}
                break

    if disease_info:
        sections.append(f"Categoria de enfermedad: {disease_info.get('categoria', 'No clasificada')}")

    # --- Seccion 2: Evidencia cientifica (si existe) ---
    if pubmed_results or chembl_results or research_report:
        sections.append("\n=== EVIDENCIA CIENTIFICA ===")
        if pubmed_results:
            sections.append(f"Articulos PubMed encontrados: {len(pubmed_results)}")
        if chembl_results:
            sections.append(f"Moléculas ChEMBL encontradas: {len(chembl_results)}")
        if research_report:
            summary = research_report.get('summary', {})
            sections.append(f"Score de relevancia: {summary.get('relevance_score', 'N/A')}/100")
            exec_summary = summary.get('executive_summary', '')
            if exec_summary:
                sections.append(f"Resumen ejecutivo: {exec_summary[:500]}")

    # --- Seccion 3: Criterios de reposicionamiento ---
    repurposing_criteria = domain_knowledge.get("criterios_reposicionamiento", {})
    if repurposing_criteria:
        sections.append("\n=== CRITERIOS DE REPOSICIONAMIENTO ===")
        sections.append(f"Score minimo para PROCEED: {repurposing_criteria.get('score_proceed', 75)}/100")
        sections.append(f"Score minimo para REFINE: {repurposing_criteria.get('score_refine', 50)}/100")

    return "\n".join(sections)


def clear_prompt_cache() -> None:
    """Clear the system prompt cache."""
    _PROMPT_CACHE.clear()
    logger.info("System prompt cache cleared")


def clear_domain_cache() -> None:
    """Clear the domain knowledge cache."""
    global _DOMAIN_CACHE
    _DOMAIN_CACHE = None
    logger.info("Domain knowledge cache cleared")
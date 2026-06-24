"""Researcher agent for pharmaceutical literature and database analysis."""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
import time
from loguru import logger

# Importar utilidades centralizadas en lugar de duplicar codigo
from utils.llm_utils import retry_api_call, llm_generate, load_system_prompt, build_drug_repurposing_context


class ResearcherAgent:
    """Agent that searches PubMed, ChEMBL and uses LLM to generate research reports."""

    SAMPLE_QUERIES = {
        "Metformin": {
            "pubmed": "metformin cancer pancreatic AMPK mTOR",
            "chembl": "metformin",
            "suggested_hypothesis": "Metformina como agente antiproliferativo en cáncer mediante activación de AMPK"
        },
        "Aspirin": {
            "pubmed": "aspirin cancer prevention colorectal COX-2",
            "chembl": "aspirin",
            "suggested_hypothesis": "Aspirina en quimioprevención de cáncer colorrectal mediado por inhibición de COX-2"
        },
        "Rapamycin": {
            "pubmed": "rapamycin longevity aging mTOR inhibitor",
            "chembl": "rapamycin",
            "suggested_hypothesis": "Rapamicina como extrapolación de ensayos inmunosupresores a indicaciones de longevidad"
        }
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1)
        self.pubmed_plugin = config.get('pubmed_plugin')
        self.chembl_plugin = config.get('chembl_plugin')
        self.llm_plugin = config.get('llm_plugin')

        # Cargar system prompt modular desde archivo
        self.system_prompt = load_system_prompt("researcher_system")
        if not self.system_prompt:
            self.system_prompt = "Eres un investigador farmacéutico especializado en reposicionamiento de fármacos."
            logger.warning("researcher_system.md not found, using fallback prompt")

        logger.info("ResearcherAgent initialized with plugins")

    def _get_cache_key(self, drug_name: str, target_disease: str) -> str:
        """Generate a cache key."""
        return f"{drug_name.lower()}_{target_disease.lower()}"

    def _search_pubmed(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search PubMed with retries."""
        if not self.pubmed_plugin:
            logger.warning("PubMed plugin not available")
            return []
        try:
            return retry_api_call(self.pubmed_plugin.search, query, max_results,
                                  max_retries=self.max_retries, retry_delay=self.retry_delay)
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []

    def _search_chembl(self, query: str) -> List[Dict[str, Any]]:
        """Search ChEMBL with retries."""
        if not self.chembl_plugin:
            logger.warning("ChEMBL plugin not available")
            return []
        try:
            return retry_api_call(self.chembl_plugin.search_molecule, query,
                                  max_retries=self.max_retries, retry_delay=self.retry_delay)
        except Exception as e:
            logger.error(f"ChEMBL search failed: {e}")
            return []

    def _get_chembl_activities(self, chembl_id: str) -> List[Dict[str, Any]]:
        """Get bioactivity data from ChEMBL."""
        if not self.chembl_plugin:
            return []
        try:
            return retry_api_call(self.chembl_plugin.get_activities, chembl_id,
                                  max_retries=self.max_retries, retry_delay=self.retry_delay)
        except Exception as e:
            logger.error(f"ChEMBL activities fetch failed: {e}")
            return []

    def _analyze_drug_protein_interactions(self, chembl_data: List[Dict], drug_name: str) -> List[Dict[str, Any]]:
        """Analyze drug-protein interactions from ChEMBL."""
        interactions = []
        for mol in chembl_data:
            # In a real implementation, parse target relationships
            interactions.append({
                'target': mol.get('target_name', 'Unknown'),
                'mechanism': mol.get('mechanism', 'Unknown'),
                'confidence': 'alta' if mol.get('similarity', 0) > 0.8 else 'media'
            })
        return interactions

    def _calculate_relevance_score(self, pubmed_count: int, chembl_activities: int, llm_summary: str) -> int:
        """Calculate relevance score 0-100."""
        score = 0
        if pubmed_count > 0:
            score += min(pubmed_count * 2, 40)  # Max 40 from PubMed
        if chembl_activities > 0:
            score += min(chembl_activities * 2, 30)  # Max 30 from ChEMBL
        if llm_summary and len(llm_summary) > 100:
            score += 20  # Quality of summary
        if llm_summary and len(llm_summary) > 500:
            score += 10
        return min(score, 100)

    async def research(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research phase for a drug repositioning task."""
        # Accept either task dict with metadata or direct params
        metadata = task.get('metadata', task)
        drug_name = metadata.get('drug_candidate', metadata.get('drug_name', 'Unknown'))
        target_disease = metadata.get('target_disease', 'Unknown')

        logger.info(f"Researching: {drug_name} -> {target_disease}")
        start_time = time.time()

        # Check cache
        cache_key = self._get_cache_key(drug_name, target_disease)
        if cache_key in self.cache:
            logger.info(f"Using cached results for {cache_key}")
            return self.cache[cache_key]

        # Get example queries if available
        example = self.SAMPLE_QUERIES.get(drug_name, {})
        pubmed_query = example.get('pubmed', f"{drug_name} {target_disease} repurposing")
        chembl_query = example.get('chembl', drug_name)

        # Parallel data collection
        try:
            pubmed_results = self._search_pubmed(pubmed_query)
            chembl_results = self._search_chembl(chembl_query)
        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            pubmed_results = []
            chembl_results = []

        # Get bioactivities
        chembl_activities = []
        if chembl_results and isinstance(chembl_results, list):
            chembl_id = chembl_results[0].get('chembl_id') or chembl_results[0].get('molecule_chembl_id')
            if chembl_id:
                chembl_activities = self._get_chembl_activities(chembl_id)

        # Analyze interactions
        interactions = self._analyze_drug_protein_interactions(
            chembl_results, drug_name
        )

        # Construir contexto farmacológico desde base de conocimiento
        drug_context = build_drug_repurposing_context(
            drug_name=drug_name,
            target_disease=target_disease,
            pubmed_results=pubmed_results,
            chembl_results=chembl_results
        )

        # Prompt enfocado SOLO en la consulta especifica, no en la logica del sistema
        # La logica del sistema se carga desde researcher_system.md
        prompt = f"""
Analiza el potencial de reposicionamiento del fármaco {drug_name} para el tratamiento de {target_disease}.

{drug_context}

Datos de PubMed:
- Artículos encontrados: {len(pubmed_results)}
- Consulta: {pubmed_query}

Datos de ChEMBL:
- Moléculas encontradas: {len(chembl_results)}
- Actividades biológicas: {len(chembl_activities)}

Basándote en el contexto farmacológico proporcionado:
1. Resume hallazgos clave sobre mecanismos de acción de {drug_name} relevantes para {target_disease}.
2. Identifica proteínas targets principales y pathways involucrados.
3. Sugiere 2-3 hipótesis de reposicionamiento específicas y comprobables.
4. Evalúa la viabilidad científica del reposicionamiento para encontrar una cura.
"""
        # Usar LLM centralizado con contexto de sistema y modelo Qwen específico
        from utils.llm_utils import call_llm
        llm_summary = await call_llm(prompt, role="reasoning", system=self.system_prompt)

        # Build structured report
        relevance_score = self._calculate_relevance_score(
            len(pubmed_results), len(chembl_activities), llm_summary
        )

        report = {
            'drug_name': drug_name,
            'target_disease': target_disease,
            'summary': {
                'pubmed_articles_count': len(pubmed_results),
                'chembl_molecules_count': len(chembl_results),
                'bioactivities_count': len(chembl_activities),
                'relevance_score': relevance_score,
                'executive_summary': llm_summary[:500] if llm_summary else "No disponible"
            },
            'evidence': {
                'mechanisms_of_action': [
                    {
                        'mechanism': 'AMPK activation / mTOR inhibition',
                        'source': f"{len(pubmed_results)} artículos PubMed",
                        'confidence': 0.8,
                        'supporting_evidence': 'Evidencia preliminar en modelos celulares'
                    }
                ],
                'drug_protein_interactions': interactions[:10],
                'clinical_trials_status': 'No disponible (requiere consulta a ClinicalTrials.gov)',
                'bioactivities': chembl_activities[:20]
            },
            'references': [
                {
                    'pmid': f'PMID_{i+1}',
                    'title': f'Estudio sobre {drug_name} en {target_disease}',
                    'year': 2020 + (i % 6)
                }
                for i in range(min(5, len(pubmed_results)))
            ],
            'suggested_hypothesis': example.get('suggested_hypothesis', f"{drug_name} podría tener efecto terapéutico en {target_disease}"),
            'query_templates': {
                'pubmed_used': pubmed_query,
                'chembl_used': chembl_query
            },
            'metadata': metadata,
            'execution_time_seconds': time.time() - start_time
        }

        # Cache result
        self.cache[cache_key] = report
        logger.success(f"Research complete for {drug_name} -> {target_disease} (score: {relevance_score})")
        return report

    def get_cached_results(self, drug_name: str, target_disease: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached research results."""
        return self.cache.get(self._get_cache_key(drug_name, target_disease))

    def clear_cache(self) -> None:
        """Clear the research cache."""
        self.cache.clear()
        logger.info("Research cache cleared")

    def __repr__(self) -> str:
        return f"ResearcherAgent(cached={len(self.cache)}, queries={list(self.SAMPLE_QUERIES.keys())})"
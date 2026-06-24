"""Refiner agent - Optimizador iterativo de pipelines de reposicionamiento farmacéutico.
Inspirado en Sakana FuGU: early stopping, loop engineering, refinamiento progresivo."""

from typing import Dict, Any, List, Optional, Tuple
import time
import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from loguru import logger

# Importar utilidades centralizadas
from utils.llm_utils import (
    retry_api_call, llm_generate, load_system_prompt,
    load_domain_knowledge, build_drug_repurposing_context
)


@dataclass
class RefinementHistory:
    """Registro del historial de refinamiento para early stopping."""
    hypothesis: str
    evaluation_score: int
    recommendation: str
    weaknesses: List[str]
    iteration: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis": self.hypothesis[:200],
            "evaluation_score": self.evaluation_score,
            "recommendation": self.recommendation,
            "weaknesses": self.weaknesses,
            "iteration": self.iteration,
            "timestamp": self.timestamp
        }


class RefinerAgent:
    """
    Agente Refiner que optimiza iterativamente hipótesis de reposicionamiento.
    
    Implementa:
    - Loop Engineering: refinamiento progresivo basado en feedback del Evaluator
    - Sakana FuGU: early stopping adaptativo, convergencia controlada
    - Análisis de causa raíz de debilidades en pipelines farmacéuticos
    """

    # Umbrales de early stopping
    DEFAULT_EARLY_STOPPING = {
        "max_iterations": 5,           # Máximo de iteraciones de refinamiento
        "score_improvement_threshold": 3,  # Mejora mínima en score para continuar
        "patience": 2,                 # Iteraciones sin mejora antes de early stop
        "min_score_to_complete": 75,   # Score mínimo para considerar "completed"
        "max_same_recommendations": 2   # Máximo de recomendaciones idénticas consecutivas
    }

    # Categorías de debilidades farmacéuticas
    WEAKNESS_CATEGORIES = [
        "bajo_rendimiento_modelo",
        "overfitting",
        "errores_ejecucion",
        "problemas_datos",
        "problemas_diseno_experimental",
        "resultados_no_concluyentes",
        "hipotesis_debil",
        "evidencia_insuficiente"
    ]

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_plugin = config.get('llm_plugin')
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1)

        # Configuración de early stopping (Sakana FuGU)
        early_stop_config = config.get('early_stopping', {})
        self.early_stopping = {**self.DEFAULT_EARLY_STOPPING, **early_stop_config}

        # Cargar system prompt modular
        self.system_prompt = load_system_prompt("refiner_system")
        if not self.system_prompt:
            self.system_prompt = (
                "Eres un optimizador experto en pipelines de fármacos computacionales. "
                "Tu misión es analizar por qué un experimento de reposicionamiento no logró "
                "resultados concluyentes y proponer mejoras concretas."
            )
            logger.warning("refiner_system.md not found, using fallback prompt")

        # Cargar umbrales desde domain_knowledge
        domain_knowledge = load_domain_knowledge()
        criterios = domain_knowledge.get("criterios_reposicionamiento", {})
        self.CONFIDENCE_THRESHOLDS = {
            "proceed": criterios.get("score_proceed", 75),
            "refine": criterios.get("score_refine", 50),
            "abort": criterios.get("score_abort", 0)
        }

        # Historial de refinamiento (Sakana FuGU: memoria de convergencia)
        self.history: List[RefinementHistory] = []
        self.best_score: int = 0
        self.best_hypothesis: Optional[str] = None
        self.no_improvement_count: int = 0
        self.consecutive_same_recs: int = 0
        self.last_recommendation: Optional[str] = None

        logger.info(
            f"RefinerAgent initialized (early_stop: "
            f"patience={self.early_stopping['patience']}, "
            f"max_iter={self.early_stopping['max_iterations']})"
        )

    def _check_early_stopping(self, current_score: int, 
                              current_recommendation: str) -> Dict[str, Any]:
        """
        Implementa early stopping adaptativo estilo Sakana FuGU.
        
        Args:
            current_score: Score de confianza de la evaluación actual
            current_recommendation: Recomendación binaria (proceed/refine/abort)
            
        Returns:
            Dict con decisión de early stopping y razón
        """
        decision = {
            "should_stop": False,
            "reason": "",
            "final_score": current_score,
            "final_recommendation": current_recommendation
        }

        # 1. Score suficiente para completar
        if current_score >= self.early_stopping["min_score_to_complete"]:
            decision["should_stop"] = True
            decision["reason"] = (
                f"Score ({current_score}) >= umbral de completado "
                f"({self.early_stopping['min_score_to_complete']})"
            )
            decision["final_recommendation"] = "proceed"
            return decision

        # 2. Máximo de iteraciones alcanzado
        total_iterations = len(self.history) + 1
        if total_iterations >= self.early_stopping["max_iterations"]:
            decision["should_stop"] = True
            decision["reason"] = (
                f"Máximo de iteraciones alcanzado "
                f"({total_iterations}/{self.early_stopping['max_iterations']})"
            )
            return decision

        # 3. Patience sin mejora significativa
        if self.history:
            last_score = self.history[-1].evaluation_score
            improvement = current_score - last_score
            if improvement < self.early_stopping["score_improvement_threshold"]:
                self.no_improvement_count += 1
            else:
                self.no_improvement_count = 0  # Reset si hay mejora

            if self.no_improvement_count >= self.early_stopping["patience"]:
                decision["should_stop"] = True
                decision["reason"] = (
                    f"Early stopping por patience: {self.no_improvement_count} "
                    f"iteraciones sin mejora significativa "
                    f"(umbral: {self.early_stopping['score_improvement_threshold']} pts)"
                )
                return decision

        # 4. Recomendaciones idénticas consecutivas (estancamiento)
        if current_recommendation == self.last_recommendation:
            self.consecutive_same_recs += 1
        else:
            self.consecutive_same_recs = 0

        if self.consecutive_same_recs >= self.early_stopping["max_same_recommendations"]:
            decision["should_stop"] = True
            decision["reason"] = (
                f"Early stopping por estancamiento: {self.consecutive_same_recs} "
                f"recomendaciones idénticas consecutivas"
            )
            return decision

        # 5. ABORT definitivo: si el score es muy bajo y no hay progreso histórico
        if current_score < 30 and len(self.history) >= 2:
            # Verificar que nunca hubo un score mejor
            all_scores = [h.evaluation_score for h in self.history] + [current_score]
            if max(all_scores) < 30:
                decision["should_stop"] = True
                decision["reason"] = (
                    f"Aborto definitivo: score máximo histórico ({max(all_scores)}) "
                    f"demasiado bajo para justificar más iteraciones"
                )
                decision["final_recommendation"] = "abort"
                return decision

        return decision

    def _extract_weaknesses(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae y clasifica debilidades del reporte de evaluación.
        
        Args:
            evaluation: Reporte del EvaluatorAgent
            
        Returns:
            Lista de debilidades estructuradas con categoría y severidad
        """
        weaknesses = []

        # Analizar validación
        validation = evaluation.get('validation', {})
        for warning in validation.get('warnings', []):
            weakness = self._classify_weakness(warning)
            weaknesses.append({
                "descripcion": warning,
                "categoria": weakness["category"],
                "severidad": "media",
                "tipo": "warning",
                "causa_raiz_sugerida": weakness["root_cause"]
            })

        for error in validation.get('errors', []):
            weaknesses.append({
                "descripcion": error,
                "categoria": self._classify_weakness(error)["category"],
                "severidad": "alta",
                "tipo": "error",
                "causa_raiz_sugerida": "Requerimiento fundamental no cumplido"
            })

        # Analizar anomalías
        for anomaly in evaluation.get('anomalies', []):
            anomaly_map = {
                "potential_overfitting": ("overfitting", "alta", "El modelo memoriza en lugar de generalizar"),
                "suspiciously_high_r2": ("overfitting", "alta", "R² anormalmente alto sugiere data leakage"),
                "suspiciously_low_rmse": ("overfitting", "alta", "RMSE anormalmente bajo"),
                "very_fast_execution": ("errores_ejecucion", "baja", "Ejecución demasiado rápida, posible fallo silencioso"),
                "no_output_artifacts": ("errores_ejecucion", "media", "No se generaron artefactos de salida"),
                "execution_errors": ("errores_ejecucion", "alta", "Errores durante la ejecución"),
                "poor_model_fit": ("bajo_rendimiento_modelo", "alta", "Modelo no logra ajustarse a los datos"),
                "suspiciously_perfect_classification": ("overfitting", "alta", "Clasificación perfecta sospechosa"),
                "execution_warnings": ("errores_ejecucion", "baja", "Advertencias durante la ejecución"),
                "low_r2": ("bajo_rendimiento_modelo", "media", "R² por debajo del rango típico")
            }
            if anomaly in anomaly_map:
                cat, severity, root_cause = anomaly_map[anomaly]
                weaknesses.append({
                    "descripcion": f"Anomalía detectada: {anomaly}",
                    "categoria": cat,
                    "severidad": severity,
                    "tipo": "anomaly",
                    "causa_raiz_sugerida": root_cause
                })

        # Analizar score de confianza
        confidence = evaluation.get('confidence_score', 0)
        if confidence < 30:
            weaknesses.append({
                "descripcion": f"Score de confianza críticamente bajo: {confidence}/100",
                "categoria": "resultados_no_concluyentes",
                "severidad": "alta",
                "tipo": "score",
                "causa_raiz_sugerida": "El pipeline completo no está produciendo resultados válidos"
            })
        elif confidence < 50:
            weaknesses.append({
                "descripcion": f"Score de confianza bajo: {confidence}/100",
                "categoria": "resultados_no_concluyentes",
                "severidad": "media",
                "tipo": "score",
                "causa_raiz_sugerida": "Resultados insuficientes para avanzar a validación experimental"
            })

        # Analizar ejecución
        exec_report = evaluation.get('execution_report', {})
        if not exec_report.get('success', False):
            weaknesses.append({
                "descripcion": "Ejecución del experimento falló",
                "categoria": "errores_ejecucion",
                "severidad": "alta",
                "tipo": "execution",
                "causa_raiz_sugerida": "Error en código, dependencias o configuración"
            })

        return weaknesses

    def _classify_weakness(self, text: str) -> Dict[str, str]:
        """
        Clasifica una debilidad en categorías del dominio farmacéutico.
        
        Args:
            text: Descripción de la debilidad
            
        Returns:
            Dict con categoría y causa raíz sugerida
        """
        text_lower = text.lower()

        # Patrones de clasificación
        patterns = [
            ("bajo_rendimiento_modelo", 
             ["r² bajo", "r2 bajo", "rmse alto", "auc bajo", "poor model", "bajo rendimiento"],
             "Métricas del modelo por debajo de umbrales aceptables"),
            ("overfitting",
             ["overfitting", "r² alto", "r2 alto", "sobreajuste", "suspiciously", "perfect"],
             "El modelo no generaliza adecuadamente a datos no vistos"),
            ("errores_ejecucion",
             ["error", "timeout", "fail", "not found", "exception", "falló", "fallo"],
             "Problemas técnicos en la ejecución del pipeline"),
            ("problemas_datos",
             ["datos", "data", "sample", "tamaño", "size", "leakage", "calidad"],
             "Calidad, cantidad o integridad de los datos insuficiente"),
            ("problemas_diseno_experimental",
             ["diseño", "design", "modelo incorrecto", "target", "supuesto"],
             "El diseño experimental no es apropiado para la pregunta biológica"),
            ("hipotesis_debil",
             ["hipótesis", "hipotesis", "hypothesis", "débil", "debil", "insuficiente"],
             "La hipótesis de reposicionamiento carece de fundamento sólido")
        ]

        for category, keywords, root_cause in patterns:
            if any(kw in text_lower for kw in keywords):
                return {"category": category, "root_cause": root_cause}

        return {"category": "resultados_no_concluyentes", 
                "root_cause": "No se pudo clasificar automáticamente"}

    def _determine_next_agent(self, weaknesses: List[Dict[str, Any]], 
                              score: int) -> str:
        """
        Determina a qué agente debe ir la siguiente iteración.
        
        Args:
            weaknesses: Lista de debilidades identificadas
            score: Score de confianza actual
            
        Returns:
            Nombre del próximo agente (researcher/designer/implementer/completed)
        """
        categories = [w["categoria"] for w in weaknesses]
        high_severity = [w for w in weaknesses if w["severidad"] == "alta"]

        # Si score es alto y sin debilidades críticas -> completed
        if score >= self.early_stopping["min_score_to_complete"] and not high_severity:
            return "completed"

        # Determinar por categoría de debilidad
        if "hipotesis_debil" in categories or "evidencia_insuficiente" in categories:
            return "researcher"
        elif "problemas_diseno_experimental" in categories:
            return "designer"
        elif "errores_ejecucion" in categories:
            return "implementer"
        elif "bajo_rendimiento_modelo" in categories:
            return "designer"  # El diseñador mejora el modelo
        elif "overfitting" in categories:
            return "designer"
        elif "problemas_datos" in categories:
            return "researcher"
        else:
            return "implementer"

    def _build_refinement_prompt(self, hypothesis: str, evaluation: Dict[str, Any],
                                 iteration: int, weaknesses: List[Dict[str, Any]],
                                 next_agent: str) -> str:
        """
        Construye el prompt de refinamiento con contexto completo.
        """
        # Estadísticas del historial
        history_summary = ""
        if self.history:
            history_lines = []
            for h in self.history[-3:]:  # Últimas 3 iteraciones
                history_lines.append(
                    f"  - Iteración {h.iteration}: score={h.evaluation_score}, "
                    f"recomendación={h.recommendation}"
                )
            history_summary = "Historial reciente:\n" + "\n".join(history_lines)

        # Debilidades formateadas
        weaknesses_formatted = ""
        if weaknesses:
            for w in weaknesses:
                weaknesses_formatted += (
                    f"- [{w['severidad'].upper()}] {w['categoria']}: "
                    f"{w['descripcion']}\n"
                )

        # Mejores resultados históricos
        best_info = ""
        if self.best_hypothesis:
            best_info = (
                f"Mejor score histórico: {self.best_score}/100\n"
                f"Mejor hipótesis previa: {self.best_hypothesis[:300]}"
            )

        prompt = f"""
=== TAREA DE REFINAMIENTO (Iteración {iteration}) ===

=== HIPÓTESIS ACTUAL ===
{hypothesis}

=== REPORTE DE EVALUACIÓN ===
Score de confianza: {evaluation.get('confidence_score', 0)}/100
Recomendación: {evaluation.get('binary_recommendation', 'N/A')}
Modelo: {evaluation.get('model_type', 'N/A')}
Fármaco: {evaluation.get('drug', 'N/A')}
Enfermedad: {evaluation.get('disease', 'N/A')}

=== DEBILIDADES IDENTIFICADAS ===
{weaknesses_formatted or "No se identificaron debilidades específicas."}

=== MÉTRICAS ===
{json.dumps(evaluation.get('metrics', {}), indent=2, ensure_ascii=False)}

=== INTERPRETACIÓN DEL EVALUADOR ===
{evaluation.get('interpretation', 'No disponible')}

=== RECOMENDACIÓN DEL EVALUADOR ===
{evaluation.get('recommendation_details', 'No disponible')}

=== PRÓXIMO AGENTE SUGERIDO ===
{next_agent}

{history_summary}

{best_info}

=== INSTRUCCIONES ===
Analiza este reporte de evaluación y genera un plan de refinamiento estructurado:

1. **Análisis de Causa Raíz**: Para cada debilidad identificada, explica su origen
2. **Plan de Mejora**: Cambios específicos en código, datos o configuración
3. **Hipótesis Refinada**: Versión mejorada de la hipótesis de reposicionamiento
4. **Hiperparámetros Sugeridos**: Valores concretos para el próximo experimento
5. **Próximo Agente**: Confirma o corrige el agente sugerido ({next_agent})

Formato de respuesta requerido:
```json
{{
  "analisis_causa_raiz": ["causa 1", "causa 2", ...],
  "plan_mejora": ["mejora 1", "mejora 2", ...],
  "hipotesis_refinada": "nueva hipótesis más específica y comprobable",
  "hiperparametros_sugeridos": {{"param": "valor", ...}},
  "proximo_agente": "researcher|designer|implementer|completed",
  "confianza_refinamiento": 0-100
}}
```
Responde EXACTAMENTE en ese formato JSON.
"""
        return prompt

    def _parse_refinement_response(self, response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del LLM extrayendo el JSON estructurado.
        """
        if not response:
            return self._default_refinement_plan()

        # Intentar extraer bloque JSON
        try:
            # Buscar entre ```json ... ``` o ``` ... ```
            import re
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Intentar parse directo
            return json.loads(response)
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Failed to parse JSON from LLM response, using fallback")
            return self._default_refinement_plan()

    def _default_refinement_plan(self) -> Dict[str, Any]:
        """Plan de refinamiento por defecto cuando falla el parseo."""
        return {
            "analisis_causa_raiz": ["No se pudo extraer análisis automático"],
            "plan_mejora": ["Revisar configuración del pipeline", "Verificar calidad de datos"],
            "hipotesis_refinada": "Reintentar con configuración optimizada",
            "hiperparametros_sugeridos": {"learning_rate": 0.001, "epochs": 100},
            "proximo_agente": "implementer",
            "confianza_refinamiento": 30
        }

    def _update_history(self, hypothesis: str, score: int, recommendation: str,
                        weaknesses: List[str], iteration: int) -> None:
        """Actualiza el historial de refinamiento."""
        entry = RefinementHistory(
            hypothesis=hypothesis,
            evaluation_score=score,
            recommendation=recommendation,
            weaknesses=[w["categoria"] for w in weaknesses],
            iteration=iteration
        )
        self.history.append(entry)

        # Actualizar mejor score
        if score > self.best_score:
            self.best_score = score
            self.best_hypothesis = hypothesis

        self.last_recommendation = recommendation
        logger.info(f"History updated: iter={iteration}, score={score}, best={self.best_score}")

    def _generate_refinement_artifacts(self, refinement_plan: Dict[str, Any],
                                       next_agent: str, iteration: int) -> Dict[str, Any]:
        """Genera artefactos de salida del refinamiento."""
        return {
            "refined_hypothesis": refinement_plan.get("hipotesis_refinada", ""),
            "improvement_plan": refinement_plan.get("plan_mejora", []),
            "root_causes": refinement_plan.get("analisis_causa_raiz", []),
            "suggested_hyperparameters": refinement_plan.get("hiperparametros_sugeridos", {}),
            "next_agent": next_agent,
            "refinement_confidence": refinement_plan.get("confianza_refinamiento", 50),
            "refinement_iteration": iteration,
            "early_stopping_info": {
                "total_iterations": len(self.history),
                "best_score": self.best_score,
                "no_improvement_count": self.no_improvement_count
            }
        }

    async def refine(self, hypothesis: str, evaluation: Dict[str, Any],
                     iteration: int) -> Dict[str, Any]:
        """
        Refina una hipótesis basándose en la evaluación del EvaluatorAgent.
        
        Args:
            hypothesis: Hipótesis de reposicionamiento actual
            evaluation: Reporte completo del EvaluatorAgent
            iteration: Número de iteración actual
            
        Returns:
            Dict con hipótesis refinada, plan de mejora y decisión de early stopping
        """
        start_time = time.time()
        logger.info(f"Refining hypothesis (iteration {iteration})")

        # Extraer score y recomendación
        current_score = evaluation.get('confidence_score', 0)
        current_rec = evaluation.get('binary_recommendation', 'refine')

        # Extraer y clasificar debilidades
        weaknesses = self._extract_weaknesses(evaluation)

        # Determinar próximo agente
        next_agent = self._determine_next_agent(weaknesses, current_score)

        # Actualizar historial
        self._update_history(
            hypothesis, current_score, current_rec, weaknesses, iteration
        )

        # Verificar early stopping (Sakana FuGU)
        early_stop = self._check_early_stopping(current_score, current_rec)
        if early_stop["should_stop"]:
            logger.info(
                f"Early stopping triggered: {early_stop['reason']} "
                f"(score={current_score})"
            )
            return {
                "refined_hypothesis": hypothesis,
                "improvement_plan": [],
                "root_causes": [f"Early stopping: {early_stop['reason']}"],
                "suggested_hyperparameters": {},
                "next_agent": "completed" if early_stop["final_recommendation"] == "proceed" else "abort",
                "refinement_confidence": current_score,
                "refinement_iteration": iteration,
                "early_stopping_info": {
                    "total_iterations": len(self.history),
                    "best_score": self.best_score,
                    "no_improvement_count": self.no_improvement_count,
                    "stop_reason": early_stop["reason"]
                },
                "execution_time_seconds": time.time() - start_time
            }

        # Construir prompt de refinamiento
        prompt = self._build_refinement_prompt(
            hypothesis, evaluation, iteration, weaknesses, next_agent
        )

        # Generar plan de refinamiento con el LLM
        # Usar modelo Qwen específico para refinamiento
        from utils.llm_utils import call_llm
        llm_response = await call_llm(prompt, role="refiner", system=self.system_prompt)

        # Parsear respuesta
        refinement_plan = self._parse_refinement_response(llm_response)

        # Si el LLM sugiere un agente diferente, priorizarlo
        llm_suggested_agent = refinement_plan.get("proximo_agente", "")
        if llm_suggested_agent in ["researcher", "designer", "implementer", "completed"]:
            next_agent = llm_suggested_agent

        # Generar artefactos de refinamiento
        result = self._generate_refinement_artifacts(
            refinement_plan, next_agent, iteration
        )

        result["execution_time_seconds"] = time.time() - start_time
        result["metadata"] = {
            "original_hypothesis": hypothesis[:200],
            "evaluation_score": current_score,
            "evaluation_recommendation": current_rec
        }

        logger.success(
            f"Refinement complete (iter {iteration}): "
            f"next={next_agent}, confidence={current_score}"
        )
        return result

    async def refine_batch(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refina múltiples hipótesis en batch.
        
        Args:
            hypotheses: Lista de dicts con 'hypothesis', 'evaluation', 'iteration'
            
        Returns:
            Lista de resultados de refinamiento
        """
        tasks = []
        for item in hypotheses:
            task = self.refine(
                hypothesis=item.get('hypothesis', ''),
                evaluation=item.get('evaluation', {}),
                iteration=item.get('iteration', 1)
            )
            tasks.append(task)

        return await asyncio.gather(*tasks)

    def get_refinement_summary(self) -> Dict[str, Any]:
        """
        Genera resumen del proceso de refinamiento completo.
        
        Returns:
            Dict con estadísticas del historial de refinamiento
        """
        if not self.history:
            return {
                "total_iterations": 0,
                "best_score": 0,
                "best_hypothesis": None,
                "convergence_status": "not_started"
            }

        scores = [h.evaluation_score for h in self.history]
        converged = (
            self.best_score >= self.early_stopping["min_score_to_complete"]
            or self.no_improvement_count >= self.early_stopping["patience"]
        )

        return {
            "total_iterations": len(self.history),
            "best_score": self.best_score,
            "best_hypothesis": self.best_hypothesis[:300] if self.best_hypothesis else None,
            "score_progression": scores,
            "no_improvement_count": self.no_improvement_count,
            "convergence_status": "converged" if converged else "optimizing",
            "early_stopping_config": self.early_stopping,
            "history": [h.to_dict() for h in self.history[-5:]]  # Últimas 5
        }

    def reset(self) -> None:
        """Resetea el estado del refiner para un nuevo ciclo."""
        self.history.clear()
        self.best_score = 0
        self.best_hypothesis = None
        self.no_improvement_count = 0
        self.consecutive_same_recs = 0
        self.last_recommendation = None
        logger.info("RefinerAgent state reset")

    def __repr__(self) -> str:
        return (
            f"RefinerAgent(iterations={len(self.history)}, "
            f"best_score={self.best_score}, "
            f"patience={self.early_stopping['patience']})"
        )
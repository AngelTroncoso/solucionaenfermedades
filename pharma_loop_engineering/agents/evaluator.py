"""Evaluator agent for executing and assessing computational experiments."""

from typing import Dict, Any, List, Optional, Tuple
import time
import json
import subprocess
import sys
from pathlib import Path
from loguru import logger

# Importar utilidades centralizadas
from utils.llm_utils import (
    retry_api_call, llm_generate, load_system_prompt,
    load_domain_knowledge, build_drug_repurposing_context
)


class EvaluatorAgent:
    """Agent that executes generated code and evaluates results."""

    # Benchmarks ahora se cargan desde domain_knowledge.yaml
    # Se mantienen como fallback por si no existe el archivo
    KNOWN_BENCHMARKS = None

    # Umbrales ahora se cargan desde domain_knowledge.yaml
    CONFIDENCE_THRESHOLDS = None

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_plugin = config.get('llm_plugin')
        self.execution_timeout = config.get('execution_timeout', 3600)
        self.output_dir = config.get('output_dir', 'evaluation_results')
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1)

        # Cargar system prompt modular
        self.system_prompt = load_system_prompt("evaluator_system")
        if not self.system_prompt:
            self.system_prompt = "Eres un evaluador experto en farmacología computacional."
            logger.warning("evaluator_system.md not found, using fallback prompt")

        # Cargar umbrales desde base de conocimiento farmacológica
        domain_knowledge = load_domain_knowledge()
        criterios = domain_knowledge.get("criterios_reposicionamiento", {})
        self.CONFIDENCE_THRESHOLDS = {
            "proceed": criterios.get("score_proceed", 75),
            "refine": criterios.get("score_refine", 50),
            "abort": criterios.get("score_abort", 0)
        }

        # Cargar benchmarks desde domain_knowledge
        self.KNOWN_BENCHMARKS = domain_knowledge.get("benchmarks_validacion", {
            "QSAR_RandomForest": {
                "dataset": "ChEMBL kinase inhibitors",
                "typical_r2_range": [0.5, 0.8],
                "typical_rmse_range": [0.6, 1.2],
                "min_samples": 100
            },
            "docking_autodock": {
                "typical_affinity_range": [-12.0, -6.0],
                "acceptable_rmsd": 2.0,
                "min_hits": 10
            },
            "admet_lipinski": {
                "pass_rate_threshold": 0.8,
                "typical_absorption": 0.7
            }
        })

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"EvaluatorAgent initialized (umbrales: {self.CONFIDENCE_THRESHOLDS})")

    def execute_code(self, script_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute generated Python script and capture results.

        Args:
            script_path: Path to the script to execute
            config: Configuration dictionary

        Returns:
            Execution report with logs, metrics, and artifacts
        """
        start_time = time.time()
        script_path = Path(script_path)

        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return {
                'success': False,
                'error': f"Script not found: {script_path}",
                'execution_time': 0
            }

        logger.info(f"Executing script: {script_path}")

        execution_report = {
            'script': str(script_path),
            'success': False,
            'logs': [],
            'metrics': {},
            'artifacts': [],
            'errors': [],
            'warnings': [],
            'execution_time': 0,
            'config': config
        }

        try:
            # Prepare environment
            env = {
                'PYTHONPATH': str(script_path.parent),
                'CUDA_VISIBLE_DEVICES': '0' if config.get('use_gpu', False) else '-1'
            }

            # Build command
            cmd = [sys.executable, str(script_path)]

            # Execute with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=script_path.parent,
                env={**subprocess.os.environ, **env}
            )

            try:
                stdout, stderr = process.communicate(timeout=self.execution_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                execution_report['errors'].append(f"Execution timeout after {self.execution_timeout}s")
                execution_report['success'] = False
                execution_report['execution_time'] = time.time() - start_time
                return execution_report

            execution_report['logs'] = stdout.split('\n')
            execution_report['errors'] = [line for line in stderr.split('\n') if line.strip()]
            execution_report['return_code'] = process.returncode
            execution_report['success'] = process.returncode == 0

            # Parse output files
            output_dir = script_path.parent / 'output'
            if output_dir.exists():
                execution_report['artifacts'] = [
                    str(p.relative_to(script_path.parent))
                    for p in output_dir.rglob('*')
                    if p.is_file()
                ]

                # Load metrics if available
                metrics_file = output_dir / 'metrics.json'
                if metrics_file.exists():
                    with open(metrics_file) as f:
                        execution_report['metrics'] = json.load(f)

                # Load additional results
                for result_file in ['docking_results.json', 'admet_predictions.json', 'model_validation.json']:
                    result_path = output_dir / result_file
                    if result_path.exists():
                        with open(result_path) as f:
                            execution_report[result_file.replace('.json', '')] = json.load(f)

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            execution_report['errors'].append(str(e))
            execution_report['success'] = False

        execution_report['execution_time'] = time.time() - start_time
        logger.info(f"Execution completed in {execution_report['execution_time']:.2f}s, success: {execution_report['success']}")
        return execution_report

    def validate_metrics(self, metrics: Dict[str, Any], model_type: str) -> Dict[str, Any]:
        """
        Validate metrics against known benchmarks.

        Args:
            metrics: Dictionary of performance metrics
            model_type: Type of model/experiment

        Returns:
            Validation report with plausibility checks
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'anomalies': [],
            'benchmark_comparison': {}
        }

        if not metrics:
            validation['warnings'].append("No metrics provided for validation")
            return validation

        # Map model types to benchmarks
        benchmark_key = None
        for key in self.KNOWN_BENCHMARKS:
            if key.lower() in model_type.lower():
                benchmark_key = key
                break

        if not benchmark_key:
            validation['warnings'].append(f"No benchmarks available for model type: {model_type}")
            return validation

        benchmark = self.KNOWN_BENCHMARKS[benchmark_key]

        # Validate R²
        if 'r2' in metrics:
            r2 = metrics['r2']
            if 'typical_r2_range' in benchmark:
                min_r2, max_r2 = benchmark['typical_r2_range']
                if r2 < min_r2:
                    validation['warnings'].append(f"R² ({r2:.3f}) below typical range ({min_r2}-{max_r2})")
                    validation['anomalies'].append("low_r2")
                elif r2 > max_r2:
                    validation['anomalies'].append("suspiciously_high_r2")
                    validation['warnings'].append(f"R² ({r2:.3f}) above typical max ({max_r2}) - possible overfitting")

                validation['benchmark_comparison']['r2'] = {
                    'value': r2,
                    'typical_range': benchmark['typical_r2_range'],
                    'status': 'normal' if min_r2 <= r2 <= max_r2 else 'anomalous'
                }

        # Validate RMSE
        if 'rmse' in metrics:
            rmse = metrics['rmse']
            if 'typical_rmse_range' in benchmark:
                min_rmse, max_rmse = benchmark['typical_rmse_range']
                if rmse < min_rmse:
                    validation['anomalies'].append("suspiciously_low_rmse")
                elif rmse > max_rmse:
                    validation['warnings'].append(f"RMSE ({rmse:.3f}) above typical range")

        # Validate AUC-ROC if present
        if 'auc_roc' in metrics:
            auc = metrics['auc_roc']
            if auc < 0.5:
                validation['errors'].append("AUC-ROC < 0.5 indicates model is worse than random")
                validation['valid'] = False
            elif auc < 0.7:
                validation['warnings'].append(f"AUC-ROC ({auc:.3f}) is poor")

        # Check sample size
        if 'n_samples' in metrics and 'min_samples' in benchmark:
            if metrics['n_samples'] < benchmark['min_samples']:
                validation['warnings'].append(f"Sample size ({metrics['n_samples']}) below recommended ({benchmark['min_samples']})")

        validation['benchmark_comparison']['model_type'] = model_type
        validation['benchmark_comparison']['benchmark_used'] = benchmark_key

        return validation

    def detect_anomalies(self, execution_report: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """
        Detect anomalies in execution and results.

        Returns:
            List of detected anomaly types
        """
        anomalies = []

        # Check execution time anomalies
        exec_time = execution_report.get('execution_time', 0)
        if exec_time > 0 and exec_time < 1:
            anomalies.append("very_fast_execution")
        elif exec_time > 3600:
            anomalies.append("very_slow_execution")

        # Check for missing artifacts
        artifacts = execution_report.get('artifacts', [])
        if not artifacts:
            anomalies.append("no_output_artifacts")

        # Check for errors in logs
        errors = execution_report.get('errors', [])
        if errors:
            anomalies.append("execution_errors")

        # Check metrics anomalies
        if metrics:
            if 'r2' in metrics and metrics['r2'] > 0.95:
                anomalies.append("potential_overfitting")
            if 'r2' in metrics and metrics['r2'] < 0.3:
                anomalies.append("poor_model_fit")
            if 'auc_roc' in metrics and metrics['auc_roc'] > 0.99:
                anomalies.append("suspiciously_perfect_classification")

        # Check for warnings
        if execution_report.get('warnings'):
            anomalies.append("execution_warnings")

        return anomalies

    def interpret_results(self, metrics: Dict[str, Any], model_type: str, drug: str, disease: str) -> str:
        """
        Use LLM to interpret results in pharmacological context.

        Returns:
            LLM-generated interpretation
        """
        prompt = f"""
Interpreta los siguientes resultados de un experimento de reposicionamiento de fármacos:

Contexto:
- Fármaco analizado: {drug}
- Enfermedad objetivo: {disease}
- Tipo de modelo: {model_type}

Métricas obtenidas:
{json.dumps(metrics, indent=2)}

Genera una interpretación farmacológica:
1. ¿Qué significan estos resultados para el potencial de reposicionamiento?
2. ¿Los valores de las métricas son clínicamente relevantes?
3. ¿Qué limitaciones metodológicas se deben considerar?
4. ¿Qué pasos adicionales sugerirías para validar estos hallazgos?
5. ¿Existe evidencia en literatura que soporte o contradiga estos resultados?

Responde en español, de manera concisa pero técnica.
"""
        # Usar LLM centralizado con contexto de sistema
        from utils.llm_utils import llm_generate as central_llm
        return central_llm(self.llm_plugin, prompt, max_tokens=1500,
                           max_retries=self.max_retries, retry_delay=self.retry_delay)

    def generate_recommendation(self, metrics: Dict[str, Any], validation: Dict[str, Any],
                               anomalies: List[str], confidence_score: int) -> str:
        """
        Generate binary recommendation: proceed, refine, or abort.

        Returns:
            Recommendation string with justification
        """
        prompt = f"""
Basándote en la siguiente evaluación, genera una recomendación binaria:

Métricas:
{json.dumps(metrics, indent=2)}

Validación:
- Válido: {validation.get('valid', False)}
- Advertencias: {validation.get('warnings', [])}
- Errores: {validation.get('errors', [])}

Anomalías detectadas: {anomalies}
Score de confianza: {confidence_score}/100

Opciones:
1. PROCEED (score >= 75): Resultados prometedores, proceder a validación experimental
2. REFINE (score 50-74): Resultados parcialmente válidos, requieren ajustes
3. ABORT (score < 50): Resultados no concluyentes o problemas graves

Genera:
1. La recomendación binaria (PROCEED/REFINE/ABORT)
2. Justificación detallada (3-5 puntos)
3. Acciones específicas si es REFINE
4. Riesgos si es ABORT
"""
        # Usar LLM centralizado
        from utils.llm_utils import llm_generate as central_llm
        return central_llm(self.llm_plugin, prompt, max_tokens=1000,
                           max_retries=self.max_retries, retry_delay=self.retry_delay)

    def calculate_confidence_score(self, metrics: Dict[str, Any], validation: Dict[str, Any],
                                   execution_report: Dict[str, Any]) -> int:
        """
        Calculate overall confidence score (0-100).

        Returns:
            Integer confidence score
        """
        score = 50  # Base score

        # Metric quality (max +30)
        if 'r2' in metrics:
            r2 = metrics['r2']
            if r2 > 0.7:
                score += 20
            elif r2 > 0.5:
                score += 10
            elif r2 < 0.3:
                score -= 15

        if 'auc_roc' in metrics:
            auc = metrics['auc_roc']
            if auc > 0.8:
                score += 10
            elif auc > 0.7:
                score += 5
            elif auc < 0.6:
                score -= 10

        # Validation results (max +20)
        if validation.get('valid', False):
            score += 20

        # Deduct for warnings/errors
        score -= len(validation.get('warnings', [])) * 3
        score -= len(validation.get('errors', [])) * 10

        # Execution quality (max +/-10)
        if execution_report.get('success', False):
            score += 10
        else:
            score -= 20

        # Anomalies (max -20)
        anomalies = len(self.detect_anomalies(execution_report, metrics))
        score -= min(anomalies * 5, 20)

        return max(0, min(100, score))

    def evaluate(self, implementation_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main evaluation pipeline.

        Args:
            implementation_report: Report from ImplementerAgent

        Returns:
            Complete evaluation report
        """
        start_time = time.time()

        metadata = implementation_report.get('metadata', {})
        drug = metadata.get('drug_candidate', 'Unknown')
        disease = metadata.get('target_disease', 'Unknown')
        model_type = implementation_report.get('model_type', 'Unknown')

        logger.info(f"Evaluating implementation: {drug} -> {disease} ({model_type})")

        # Execute code
        main_script = implementation_report.get('main_script', '')
        execution_report = self.execute_code(main_script, implementation_report.get('config', {}))

        # Extract metrics
        metrics = execution_report.get('metrics', {})

        # Add sample count if available
        if 'train_samples' not in metrics:
            # Try to infer from logs
            logs = ' '.join(execution_report.get('logs', []))
            if 'Train:' in logs:
                try:
                    parts = logs.split('Train:')[1].split(',')[0]
                    metrics['n_samples_train'] = int(parts.strip())
                except:
                    pass

        # Validate metrics
        validation = self.validate_metrics(metrics, model_type)

        # Detect anomalies
        anomalies = self.detect_anomalies(execution_report, metrics)

        # Calculate confidence
        confidence_score = self.calculate_confidence_score(metrics, validation, execution_report)

        # LLM interpretation
        interpretation = self.interpret_results(metrics, model_type, drug, disease)

        # Generate recommendation
        recommendation = self.generate_recommendation(metrics, validation, anomalies, confidence_score)

        # Determine binary recommendation
        if confidence_score >= self.CONFIDENCE_THRESHOLDS['proceed']:
            binary_rec = 'proceed'
        elif confidence_score >= self.CONFIDENCE_THRESHOLDS['refine']:
            binary_rec = 'refine'
        else:
            binary_rec = 'abort'

        # Generate visualizations summary
        viz_summary = self._summarize_visualizations(execution_report.get('artifacts', []))

        evaluation_report = {
            'evaluation_id': f"eval_{int(time.time())}",
            'drug': drug,
            'disease': disease,
            'model_type': model_type,
            'execution_report': {
                'success': execution_report['success'],
                'execution_time_seconds': execution_report['execution_time'],
                'return_code': execution_report.get('return_code'),
                'artifacts_count': len(execution_report.get('artifacts', [])),
                'error_count': len(execution_report.get('errors', []))
            },
            'metrics': metrics,
            'validation': validation,
            'anomalies': anomalies,
            'confidence_score': confidence_score,
            'binary_recommendation': binary_rec,
            'interpretation': interpretation,
            'recommendation_details': recommendation,
            'visualizations': viz_summary,
            'execution_time_seconds': time.time() - start_time,
            'metadata': metadata
        }

        logger.success(f"Evaluation complete: {binary_rec} (score: {confidence_score})")
        return evaluation_report

    def _summarize_visualizations(self, artifacts: List[str]) -> Dict[str, Any]:
        """Summarize available visualizations."""
        viz_types = {
            'scatter': 'predicted_vs_actual.png',
            'feature_importance': 'feature_importance.png',
            'roc_curve': 'roc_curve.png',
            'confusion_matrix': 'confusion_matrix.png',
            'learning_curve': 'learning_curve.png'
        }

        found = {}
        for viz_type, filename in viz_types.items():
            matching = [a for a in artifacts if filename in a]
            if matching:
                found[viz_type] = matching[0]

        return {
            'available': list(found.keys()),
            'files': found,
            'total_visualizations': len(found)
        }

    def run_statistical_tests(self, y_true, y_pred) -> Dict[str, Any]:
        """
        Run basic statistical tests on predictions.

        Returns:
            Dictionary of test results
        """
        from scipy import stats

        tests = {}

        # Normality test (Shapiro-Wilk)
        try:
            residuals = y_true - y_pred
            shapiro_stat, shapiro_p = stats.shapiro(residuals[:min(5000, len(residuals))])
            tests['shapiro_wilk'] = {
                'statistic': float(shapiro_stat),
                'p_value': float(shapiro_p),
                'normal': shapiro_p > 0.05
            }
        except Exception as e:
            tests['shapiro_wilk'] = {'error': str(e)}

        # Correlation test (Pearson)
        try:
            pearson_r, pearson_p = stats.pearsonr(y_true, y_pred)
            tests['pearson_correlation'] = {
                'r': float(pearson_r),
                'p_value': float(pearson_p),
                'significant': pearson_p < 0.05
            }
        except Exception as e:
            tests['pearson_correlation'] = {'error': str(e)}

        # Paired t-test (if predictions are from different models)
        tests['sample_size'] = len(y_true)
        tests['mean_true'] = float(y_true.mean())
        tests['mean_pred'] = float(y_pred.mean())
        tests['bias'] = float(y_pred.mean() - y_true.mean())

        return tests

    def generate_evaluation_report(self, evaluation: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate human-readable evaluation report.

        Returns:
            Path to saved report
        """
        if output_path is None:
            output_path = Path(self.output_dir) / f"evaluation_report_{evaluation.get('evaluation_id', 'latest')}.md"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = f"""# Informe de Evaluación: {evaluation.get('drug')} para {evaluation.get('disease')}

## Resumen Ejecutivo

- **Modelo**: {evaluation.get('model_type')}
- **Score de Confianza**: {evaluation.get('confidence_score')}/100
- **Recomendación**: {evaluation.get('binary_recommendation', 'N/A').upper()}
- **Ejecución exitosa**: {evaluation.get('execution_report', {}).get('success', False)}

## Métricas de Rendimiento

| Métrica | Valor | Benchmark |
|---------|-------|-----------|
"""

        metrics = evaluation.get('metrics', {})
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                benchmark = evaluation.get('validation', {}).get('benchmark_comparison', {}).get(metric, {})
                typical = benchmark.get('typical_range', 'N/A')
                report += f"| {metric} | {value:.3f} | {typical} |\n"

        report += f"""
## Análisis de Validación

**Válido**: {evaluation.get('validation', {}).get('valid', False)}

**Advertencias**:
"""
        for warning in evaluation.get('validation', {}).get('warnings', []):
            report += f"- {warning}\n"

        report += """
**Errores**:
"""
        for error in evaluation.get('validation', {}).get('errors', []):
            report += f"- {error}\n"

        report += f"""
## Anomalías Detectadas

"""
        if evaluation.get('anomalies'):
            for anomaly in evaluation['anomalies']:
                report += f"- {anomaly}\n"
        else:
            report += "No se detectaron anomalías significativas.\n"

        report += f"""
## Interpretación de Resultados

{evaluation.get('interpretation', 'No disponible')}

## Recomendación

{evaluation.get('recommendation_details', 'No disponible')}

## Visualizaciones Generadas

"""
        viz = evaluation.get('visualizations', {})
        if viz.get('available'):
            for viz_type, filename in viz.get('files', {}).items():
                report += f"- **{viz_type}**: {filename}\n"
        else:
            report += "No se generaron visualizaciones.\n"

        report += f"""
## Próximos Pasos

"""
        rec = evaluation.get('binary_recommendation', 'abort')
        if rec == 'proceed':
            report += """
1. Realizar validación experimental en laboratorio
2. Preparar compuestos para ensayos in vitro
3. Documentar protocolo para reproducibilidad
4. Considerar publicación de resultados preliminares
"""
        elif rec == 'refine':
            report += """
1. Revisar calidad de datos de entrenamiento
2. Ajustar hiperparámetros del modelo
3. Considerar técnicas de regularización
4. Aumentar tamaño de dataset si es posible
5. Evaluar arquitecturas alternativas (GNN, Deep Learning)
"""
        else:
            report += """
1. Revisar diseño experimental
2. Verificar calidad de datos de entrada
3. Considerar supuestos del modelo
4. Evaluar factibilidad del enfoque
5. Explorar modelos alternativos
"""

        report += f"""
---
Generado automáticamente por EvaluatorAgent
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.success(f"Evaluation report saved to {output_path}")
        return str(output_path)

    def get_quick_status(self, execution_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get quick status summary without full evaluation.

        Returns:
            Quick status dictionary
        """
        return {
            'execution_success': execution_report.get('success', False),
            'has_errors': bool(execution_report.get('errors')),
            'has_artifacts': bool(execution_report.get('artifacts')),
            'execution_time': execution_report.get('execution_time', 0),
            'metrics_available': bool(execution_report.get('metrics'))
        }

    def __repr__(self) -> str:
        return f"EvaluatorAgent(llm={'available' if self.llm_plugin else 'unavailable'}, timeout={self.execution_timeout}s)"
"""Designer agent for creating computational experiment plans."""

from typing import Dict, Any, List, Optional
import time
from loguru import logger


class DesignAgent:
    """Agent that designs computational experiments for drug repositioning."""

    POTENTIAL_TARGETS = {
        "cancer": {
            "targets": ["PI3K/mTOR", "EGFR", "VEGFR", "CDK4/6", "PARP"],
            "models": ["docking", "QSAR", "molecular_dynamics"]
        },
        "fibrosis": {
            "targets": ["TGF-beta receptor", "MMPs", "TNF-alpha", "PDGF receptor"],
            "models": ["docking", "pharmacophore", "QSAR"]
        },
        "viral_infection": {
            "targets": ["viral_protease", "polymerase", "hemagglutinin", "neuraminidase"],
            "models": ["docking", "QSAR", "deep_learning"]
        },
        "preeclampsia": {
            "targets": ["eNOS", "sGC", "VEGFR1", "PlGF"],
            "models": ["docking", "molecular_dynamics", "pharmacophore"]
        },
        "liver_disease": {
            "targets": ["PPAR-alpha", "FXR", "TGF-beta", "Caspases"],
            "models": ["QSAR", "docking", "ADMET_prediction"]
        }
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_plugin = config.get('llm_plugin')
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1)
        self.default_environment = config.get('environment', 'local')

        logger.info("DesignAgent initialized")

    def _get_retry_api_call(self, func, *args, **kwargs):
        """Retry API calls with exponential backoff."""
        import time
        attempt = 0
        last_error = None
        while attempt < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                attempt += 1
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        raise last_error

    def _llm_generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text with LLM with retries."""
        if not self.llm_plugin:
            logger.warning("LLM plugin not available")
            return "LLM no disponible - diseño basado en reglas predefinidas"
        try:
            return self._get_retry_api_call(self.llm_plugin.generate_text, prompt, max_tokens)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error en generación LLM: {e}"

    def _select_target(self, disease_area: str, drug_name: str) -> Dict[str, Any]:
        """Select molecular target based on disease area."""
        disease_key = None
        for key in self.POTENTIAL_TARGETS:
            if key.lower() in disease_area.lower():
                disease_key = key
                break

        if not disease_key:
            disease_key = "cancer"  # Default fallback

        targets = self.POTENTIAL_TARGETS[disease_key]["targets"]
        selected = targets[0]  # Primary target

        return {
            "primary_target": selected,
            "alternative_targets": targets[1:],
            "target_family": selected.split("/")[0],
            "rationale": f"Target seleccionado basado en patologías de {disease_area}"
        }

    def _select_model(self, target_info: Dict, disease_area: str) -> Dict[str, Any]:
        """Select computational model."""
        models = self.POTENTIAL_TARGETS.get(
            next((k for k in self.POTENTIAL_TARGETS if k in disease_area.lower()), "cancer")
        )["models"]

        return {
            "primary_model": models[0],
            "secondary_models": models[1:] if len(models) > 1 else [],
            "model_rationale": f"Modelo {models[0]} apropiado para objetivo molecular {target_info['primary_target']}"
        }

    def _select_algorithms(self, model_type: str, data_availability: str) -> Dict[str, Any]:
        """Select ML/DL algorithms."""
        algorithm_map = {
            "docking": {
                "algorithms": ["AutoDock Vina", "GNINA", "GoldScore"],
                "ml_backend": "Random Forest para rescoring"
            },
            "QSAR": {
                "algorithms": ["Random Forest", "XGBoost", "SVM", "Deep DNN"],
                "ml_backend": "scikit-learn"
            },
            "molecular_dynamics": {
                "algorithms": ["GROMACS", "AMBER", "OpenMM"],
                "ml_backend": "GNN para análisis de trayectorias"
            },
            "deep_learning": {
                "algorithms": ["Graph Transformer", "GNN", "CNN-3D"],
                "ml_backend": "PyTorch Geometric"
            },
            "pharmacophore": {
                "algorithms": ["Phase", "Catalyst", "Pharmit"],
                "ml_backend": "Random Forest para validación"
            }
        }

        selection = algorithm_map.get(model_type, algorithm_map["QSAR"])
        return {
            "primary_algorithm": selection["algorithms"][0],
            "alternative_algorithms": selection["algorithms"][1:],
            "ml_backend": selection["ml_backend"],
            "justification": f"Seleccionado por rendimiento en tareas de {model_type}"
        }

    def _define_metrics(self, model_type: str, disease: str) -> Dict[str, Any]:
        """Define evaluation metrics."""
        base_metrics = {
            "docking": {
                "binding_affinity": {"unit": "kcal/mol", "threshold": -9.0, "direction": "lower_is_better"},
                "rmsd": {"unit": "Å", "threshold": 2.0, "direction": "lower_is_better"},
                "hydrogen_bonds": {"unit": "count", "threshold": 3, "direction": "higher_is_better"}
            },
            "QSAR": {
                "ic50_predicted": {"unit": "μM", "threshold": "< 10", "direction": "lower_is_better"},
                "r2_score": {"unit": "", "threshold": "> 0.7", "direction": "higher_is_better"},
                "rmse": {"unit": "log units", "threshold": "< 0.8", "direction": "lower_is_better"}
            },
            "molecular_dynamics": {
                "rmsd": {"unit": "Å", "threshold": "< 3.0", "direction": "lower_is_better"},
                "binding_energy_mmpbsa": {"unit": "kcal/mol", "threshold": "< -40", "direction": "lower_is_better"},
                "hydrogen_bond_persistence": {"unit": "%", "threshold": "> 60", "direction": "higher_is_better"}
            },
            "deep_learning": {
                "auc_roc": {"unit": "", "threshold": "> 0.85", "direction": "higher_is_better"},
                "precision": {"unit": "", "threshold": "> 0.80", "direction": "higher_is_better"},
                "recall": {"unit": "", "threshold": "> 0.75", "direction": "higher_is_better"}
            },
            "pharmacophore": {
                "fit_score": {"unit": "", "threshold": "> 70", "direction": "higher_is_better"},
                "false_positives": {"unit": "%", "threshold": "< 20", "direction": "lower_is_better"}
            }
        }

        metrics = base_metrics.get(model_type, base_metrics["QSAR"])
        return metrics

    def _define_data_requirements(self, model_type: str, target: str) -> Dict[str, Any]:
        """Define data requirements and sources."""
        data_map = {
            "docking": {
                "required": [
                    {"name": "protein_structure", "source": "PDB/AlphaFoldDB", "format": "PDB"},
                    {"name": "ligand_smiles", "source": "ChEMBL/ZINC", "format": "SMI"},
                    {"name": "reference_ligands", "source": "ChEMBL", "format": "SDF"}
                ]
            },
            "QSAR": {
                "required": [
                    {"name": "bioactivity_data", "source": "ChEMBL/PubChem", "format": "CSV"},
                    {"name": "molecular_descriptors", "source": "RDKit/Mordred", "format": "CSV"},
                    {"name": "fingerprints", "source": "RDKit", "format": "NPZ"}
                ]
            },
            "molecular_dynamics": {
                "required": [
                    {"name": "protein_structure", "source": "PDB/AlphaFoldDB", "format": "PDB"},
                    {"name": "force_field", "source": "AMBER/CHARMM", "format": "parameters"},
                    {"name": "simulation_time", "source": "user_defined", "format": "ns"}
                ]
            },
            "deep_learning": {
                "required": [
                    {"name": "graph_data", "source": "ChEMBL/ZINC", "format": "pt"},
                    {"name": "pretrained_weights", "source": "Model Zoo", "format": "pth"},
                    {"name": "train_val_split", "source": "internal", "format": "json"}
                ]
            },
            "pharmacophore": {
                "required": [
                    {"name": "actives", "source": "ChEMBL", "format": "SDF"},
                    {"name": "protein_pocket", "source": "PDB", "format": "PDB"},
                    {"name": "pharmacophore_model", "source": "Phase/Catalyst", "format": "pha"}
                ]
            }
        }

        return data_map.get(model_type, data_map["QSAR"])

    def _estimate_resources(self, model_type: str, dataset_size: int = 1000) -> Dict[str, Any]:
        """Estimate computational resources."""
        estimates = {
            "docking": {
                "cpu": "4-8 cores",
                "ram_gb": "16-32",
                "gpu": "Opcional (aceleración 10x)",
                "storage_gb": "10-50",
                "estimated_hours": 4
            },
            "QSAR": {
                "cpu": "2-4 cores",
                "ram_gb": "8-16",
                "gpu": "No requerido",
                "storage_gb": "5-20",
                "estimated_hours": 2
            },
            "molecular_dynamics": {
                "cpu": "8-16 cores",
                "ram_gb": "32-64",
                "gpu": "Recomendado (reducción 50x tiempo)",
                "storage_gb": "50-200",
                "estimated_hours": 24
            },
            "deep_learning": {
                "cpu": "4-8 cores",
                "ram_gb": "16-32",
                "gpu": "Recomendado (CUDA 11+)",
                "storage_gb": "20-100",
                "estimated_hours": 8
            },
            "pharmacophore": {
                "cpu": "2-4 cores",
                "ram_gb": "8-16",
                "gpu": "No requerido",
                "storage_gb": "5-15",
                "estimated_hours": 3
            }
        }
        return estimates.get(model_type, estimates["QSAR"])

    def _define_timeline(self, model_type: str) -> Dict[str, Any]:
        """Define estimated timeline."""
        phases = {
            "docking": {
                "setup": "1h",
                "data_prep": "2h",
                "execution": "4h",
                "analysis": "2h",
                "total_hours": 9
            },
            "QSAR": {
                "setup": "30m",
                "data_prep": "1h",
                "execution": "2h",
                "analysis": "1h",
                "total_hours": 4.5
            },
            "molecular_dynamics": {
                "setup": "2h",
                "data_prep": "3h",
                "execution": "24h",
                "analysis": "4h",
                "total_hours": 33
            },
            "deep_learning": {
                "setup": "1h",
                "data_prep": "2h",
                "execution": "8h",
                "analysis": "3h",
                "total_hours": 14
            },
            "pharmacophore": {
                "setup": "30m",
                "data_prep": "1h",
                "execution": "3h",
                "analysis": "1h",
                "total_hours": 5.5
            }
        }
        return phases.get(model_type, phases["QSAR"])

    def _library_requirements(self, model_type: str) -> List[str]:
        """Define Python library requirements."""
        base_libs = ["numpy", "pandas", "scikit-learn", "loguru", "requests"]

        model_libs = {
            "docking": ["rdkit", "openbabel", "meeko", "pyrmsd"],
            "QSAR": ["rdkit", "mordred", "xgboost", "lightgbm", "matplotlib", "seaborn"],
            "molecular_dynamics": ["openmm", "MDAnalysis", "pytraj", "parmed"],
            "deep_learning": ["torch", "torch-geometric", "transformers", "datamol"],
            "pharmacophore": ["rdkit", "opentox", "pharmacophore"]
        }

        return base_libs + model_libs.get(model_type, [])

    def _validate_environment(self, libraries: List[str], resources: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if design is executable in available environment."""
        validation = {
            "feasible_local": True,
            "feasible_colab": True,
            "missing_libraries": [],
            "bottlenecks": []
        }

        # Check for GPU-heavy libraries
        gpu_libs = ["torch", "tensorflow", "openmm"]
        needs_gpu = any(lib in libraries for lib in gpu_libs)

        if needs_gpu:
            validation["bottlenecks"].append("GPU requerida para optimización de rendimiento")
            validation["feasible_local"] = validation["feasible_local"] and "GPU" in resources.get("gpu", "")
            validation["feasible_colab"] = True  # Colab always has GPU

        # Check memory requirements
        try:
            ram_gb = int(resources.get("ram_gb", "8").split("-")[-1])
            if ram_gb > 64:
                validation["feasible_local"] = False
                validation["bottlenecks"].append(f"Requiere {ram_gb}GB RAM (disponible típicamente 16-32GB en local)")
        except:
            pass

        return validation

    def _generate_experiment_flowchart(self, model_type: str) -> str:
        """Generate experiment flowchart description."""
        flowcharts = {
            "docking": """
            📊 Diagrama de Flujo - Docking Molecular
            ┌─────────────────┐
            │ Protein Target  │ (AlphaFold/PDB)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Preparación    │ (AddH, Minimización)
            │   Proteína      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Ligand Library  │ (ChEMBL/ZINC)
            │   (SMILES)      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Generación     │ (RDKit)
            │  Conformaciones │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   Docking       │ (AutoDock Vina/
            │   Screening     │  GNINA)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Rescoring &     │ (RF/GBSA)
            │  Filtrado       │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Top Hits        │ (Binding affinity < -9 kcal/mol)
            └─────────────────┘
            """,
            "QSAR": """
            📊 Diagrama de Flujo - Modelo QSAR
            ┌─────────────────┐
            │ Bioactivity Data│ (ChEMBL IC50/EC50)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Data Cleaning   │ (Falta valores, duplicados)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Descripción     │ (RDKit: fingerprints,
            │  Molecular      │  descriptores topológicos)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Train/Val/Test  │ (70/15/15 split)
            │    Split        │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Model Training  │ (Random Forest/
            │                 │  XGBoost/GNN)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Validation      │ (R² > 0.7, RMSE < 0.8)
            │   Metrics       │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Virtual         │ (Screen compound
            │  Screening      │  library)
            └─────────────────┘
            """,
            "default": """
            📊 Diagrama de Flujo - Diseño Experimental
            ┌─────────────────┐
            │ Investigación   │ (PubMed/ChEMBL)
            │   Preliminar    │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Selección       │ (Target + Modelo
            │   Metodología   │  computacional)
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Preparación     │ (Datos/Librerías)
            │   de Datos      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Ejecución      │ (Pipeline principal)
            │   Computacional │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Validación de   │ (Criterios cuantificables)
            │   Resultados    │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Iteración o     │ (Refinamiento)
            │   Finalización  │
            └─────────────────┘
            """
        }
        return flowcharts.get(model_type, flowcharts["default"])

    def design(self, research_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate design document from research report."""
        start_time = time.time()

        # Extract context from research report
        metadata = research_report.get('metadata', {})
        disease = metadata.get('target_disease', 'Unknown')
        drug = metadata.get('drug_candidate', metadata.get('drug_name', 'Unknown'))

        logger.info(f"Designing experiment for {drug} -> {disease}")

        # Determine disease area
        disease_area = disease
        for key in self.POTENTIAL_TARGETS:
            if key.lower() in disease.lower():
                disease_area = key
                break

        # Selection steps
        target_info = self._select_target(disease_area, drug)
        model_info = self._select_model(target_info, disease_area)
        algorithm_info = self._select_algorithms(model_info['primary_model'], 'medium')
        data_req = self._define_data_requirements(model_info['primary_model'], target_info['primary_target'])
        resources = self._estimate_resources(model_info['primary_model'])
        timeline = self._define_timeline(model_info['primary_model'])
        metrics = self._define_metrics(model_info['primary_model'], disease)

        # Flatten data requirements for summary
        data_req_list = data_req.get("required", []) if isinstance(data_req, dict) else data_req

        # LLM-enhanced design prompt
        prompt = f"""
Diseña un plan de prototipado computacional para reposicionamiento de fármacos.

Contexto:
- Fármaco: {drug}
- Enfermedad objetivo: {disease}
- Target molecular: {target_info['primary_target']}
- Modelo computacional: {model_info['primary_model']}

Genera:
1. Arquitectura detallada del experimento computacional
2. Selección de algoritmos: {algorithm_info['primary_algorithm']} (alternativas: {', '.join(algorithm_info['alternative_algorithms'])})
3. Pipeline de procesamiento de datos
4. Criterios de éxito cuantificables (IC50, binding affinity, ADMET)
5. Posibles limitaciones y mitigaciones
6. Ventajas de este enfoque vs alternativas
"""
        llm_design = self._llm_generate(prompt, max_tokens=2000)

        libraries = self._library_requirements(model_info['primary_model'])
        validation = self._validate_environment(libraries, resources)
        flowchart = self._generate_experiment_flowchart(model_info['primary_model'])

        design_doc = {
            "title": f"Diseño Experimental: {drug} para {disease}",
            "molecular_target": target_info,
            "computational_model": model_info,
            "algorithms": algorithm_info,
            "evaluation_metrics": metrics,
            "data_requirements": {
                "required_datasets": data_req,
                "sources_summary": [d["source"] for d in data_req_list]
            },
            "environment": {
                "default": self.default_environment,
                "library_requirements": libraries,
                "validation": validation
            },
            "resources": resources,
            "timeline": timeline,
            "experiment_flowchart": flowchart,
            "llm_enhanced_design": llm_design,
            "research_basis": {
                "source_report": research_report.get('summary', {}),
                "suggested_hypothesis": research_report.get('suggested_hypothesis', '')
            },
            "execution_time_seconds": time.time() - start_time,
            "metadata": metadata
        }

        logger.success(f"Design generated for {drug} -> {disease} using {model_info['primary_model']}")
        return design_doc

    def validate_design(self, design_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate design document for executability."""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": []
        }

        # Check required fields
        required_fields = ['molecular_target', 'computational_model', 'algorithms', 'evaluation_metrics']
        for field in required_fields:
            if field not in design_doc:
                validation["errors"].append(f"Missing required field: {field}")
                validation["valid"] = False

        # Check metric thresholds
        metrics = design_doc.get('evaluation_metrics', {})
        for metric_name, metric_config in metrics.items():
            if 'threshold' not in metric_config:
                validation["warnings"].append(f"Metric '{metric_name}' missing threshold")

        # Validate environment
        env_validation = design_doc.get('environment', {}).get('validation', {})
        if env_validation.get('feasible_local') is False and env_validation.get('feasible_colab') is False:
            validation["errors"].append("Design not feasible in any available environment")
            validation["valid"] = False

        return validation

    def __repr__(self) -> str:
        return f"DesignAgent(llm={'available' if self.llm_plugin else 'unavailable'}, env={self.default_environment})"
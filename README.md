<div align="center">

# 🧬 Pharma Loop Engineering

**Motor evolutivo de reposicionamiento farmacéutico con agentes multi-IA**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Qwen](https://img.shields.io/badge/LLM-Qwen%20Only-7B68EE?style=flat-square)](https://huggingface.co/Qwen)
[![Asyncio](https://img.shields.io/badge/Async-asyncio-00BCD4?style=flat-square)](https://docs.python.org/3/library/asyncio.html)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-En%20Producción-F59E0B?style=flat-square)]()

*Encuentra curas — no solo tratamientos — evolucionando hipótesis sobre combinaciones de fármacos ya aprobados*

[Ver Repositorio](https://github.com/AngelTroncoso/solucionaenfermedades) · [Reportar Bug](https://github.com/AngelTroncoso/solucionaenfermedades/issues)

</div>

---

## ✦ Qué hace

Pharma Loop Engineering implementa un **pipeline de 6 agentes de IA** para descubrir usos terapéuticos nuevos en fármacos ya aprobados por FDA/EMA. En lugar de sintetizar nuevas moléculas, el sistema analiza perfiles farmacológicos existentes y refina hipótesis iterativamente hasta alcanzar plausibilidad clínica.

**Enfermedades objetivo prioritarias:**
- 🤧 Rinitis alérgica crónica (primaveral y al polvo) — pipeline especializado con criterios ARIA 2020
- Extensible a cualquier condición Th2-mediada o inflamatoria

> **Restricción de modelos:** toda la inferencia LLM corre exclusivamente en **modelos Qwen** vía DashScope (Alibaba Cloud) o OpenRouter. Sin GPT, Claude, Gemini ni Llama.

---

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart TD
    A([🚀 main.py]) --> B[🎭 Orchestrator\nCoordina pipeline]

    B --> C[🔬 Researcher\nInvestigación inicial]
    C --> D[🎨 Designer\nDiseño de hipótesis]
    D --> E[🛠️ Implementer\nImplementación técnica]
    E --> F[⚖️ Evaluator\nEvaluación multidimensional]
    F --> G{confidence ≥ 75%?}

    G -->|✅ Sí| H[(📁 research_results/\nHipótesis publicada)]
    G -->|❌ No| I[🔁 Refiner\nMejora iterativa]

    I --> J{¿Mejoró?}
    J -->|✅ Sí| F
    J -->|❌ No| K{¿Max iteraciones?}
    K -->|❌ No| I
    K -->|✅ Sí| H

    H --> L{¿Más enfermedades\nen cola?}
    L -->|✅ Sí| B
    L -->|❌ No| M([🏁 Fin])

    style A fill:#1e3a5f,color:#fff
    style H fill:#166534,color:#fff
    style M fill:#1e3a5f,color:#fff
```

---

## 🧬 Pipeline de Rinitis Alérgica

```mermaid
flowchart LR
    subgraph ALÉRGENOS["🌿 Alérgenos detectados"]
        A1[Dermatophagoides\npolvo]
        A2[Gramíneas\nprimavera]
        A3[Olivo\nprimavera]
    end

    subgraph TH2["⚡ Cascada Th2"]
        B1[IL-4] --> B2[IL-5]
        B2 --> B3[IL-13]
        B3 --> B4[IgE]
        B4 --> B5[Mastocitos]
        B5 --> B6[Eosinófilos]
    end

    subgraph BIOMARCADORES["🔬 Biomarcadores ARIA 2020"]
        C1[FeNO]
        C2[IgE específica]
        C3[Eosinófilos nasales]
    end

    subgraph OBJETIVO["🎯 Objetivo"]
        D1[❌ Solo controlar\nsíntomas]
        D2[✅ Tolerancia\ninmunológica duradera]
    end

    ALÉRGENOS --> TH2
    TH2 --> BIOMARCADORES
    BIOMARCADORES --> OBJETIVO

    style D2 fill:#166534,color:#fff
    style D1 fill:#7f1d1d,color:#fff
```

---

## 📦 Estructura del Proyecto

```mermaid
mindmap
  root((solucionaenfermedades))
    backend/
      agents/
        researcher.py
        evaluator.py
        refiner.py
        designer.py
        implementer.py
        orchestrator.py
      config/
        settings.py
        domain_knowledge.yaml
        system_prompts/
          researcher_system.md
          evaluator_system.md
          refiner_system.md
        settings.yaml
        prompts.yaml
      data/
        drug_database/
        results/
      dashboard/
        app.py
        assets/
        components/
      plugins/
        chembl_plugin.py
        database_plugin.py
        llm_plugin.py
        pubmed_plugin.py
        visualization_plugin.py
      skills/
        analysis_skill.py
        code_generation_skill.py
        design_skill.py
        optimization_skill.py
        research_skill.py
        visualization_skill.py
      utils/
        llm_utils.py
      worktrees/
        state_manager.py
      main.py
      requirements.txt
    data/
      drug_database/
    evaluation_results/
    research_results/
    frontend/
    logs/
    .env.example
    package.json
```

---

## 🚀 Inicio Rápido

```bash
git clone https://github.com/AngelTroncoso/solucionaenfermedades.git
cd solucionaenfermedades
pip install -r requirements.txt
cp .env.example .env          # agrega tu API key de OpenRouter
python main.py
```

**Dashboard:**
```bash
# Desde el directorio backend/
cd backend
python -m streamlit run dashboard/app.py
```

**Tests:**
```bash
pytest tests/ -v --asyncio-mode=auto
```

---

## ⚙️ Configuración

```python
# config/settings.py
MODEL_REASONING   = "qwen3-235b-a22b"          # Razonamiento profundo (Researcher)
MODEL_EVALUATION  = "qwen3-32b"                # Evaluación rápida
MODEL_REFINER     = "qwen2.5-72b-instruct"    # Refinamiento detallado
MODEL_LIGHT       = "qwen2.5-7b-instruct"       # Tareas auxiliares
MODEL_EMBEDDINGS  = "text-embedding-v3"        # Búsqueda semántica

MAX_ITERATIONS    = 10
FITNESS_THRESHOLD = 0.80
POPULATION_SIZE   = 10
MUTATION_RATE     = 0.30
EARLY_STOP_ROUNDS = 3
CHECKPOINT_EVERY  = 3
```

```env
# .env
DASHSCOPE_API_KEY=your_dashscope_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_PROVIDER=dashscope  # o "openrouter"

MAX_ITERATIONS=10
FITNESS_THRESHOLD=0.80
```

---

## 🧪 Base de Fármacos Aprobados

```mermaid
classDiagram
    class ApprovedDrug {
        +String nombre
        +String DCI
        +String mecanismo_accion
        +String targets_moleculares
        +String indicaciones_aprobadas
        +String efectos_adversos
        +String estado_patente
        +String biodisponibilidad
        +String via_administracion
    }

    class Montelukast { CYSLT1 · Leucotrienos · Genérico }
    class Dupilumab { IL-4Rα · Th2 · Patente 2031 }
    class Omalizumab { IgE libre · FcεRI · Genérico 2023 }
    class Mepolizumab { IL-5 · Eosinófilos · Patente 2033 }
    class Azelastina { H1 · Tópico nasal · Genérico }
    class Ciclesonida { Glucocorticoide · Nasal · Genérico }
    class Ketotifeno { H1 + Mastocitos · Oral · Genérico }
    class Bilastina { H1 3ªGen · Oral · Patente 2034 }
    class Rupatadina { H1 + 5HT2 · Oral · Genérico 2024 }
    class Azitromicina { TNFα IL6 IL8 · Inmunomod · Genérico }

    ApprovedDrug <|-- Montelukast
    ApprovedDrug <|-- Dupilumab
    ApprovedDrug <|-- Omalizumab
    ApprovedDrug <|-- Mepolizumab
    ApprovedDrug <|-- Azelastina
    ApprovedDrug <|-- Ciclesonida
    ApprovedDrug <|-- Ketotifeno
    ApprovedDrug <|-- Bilastina
    ApprovedDrug <|-- Rupatadina
    ApprovedDrug <|-- Azitromicina
```

---


## 📊 Historial del Repositorio

```mermaid
gitGraph
   commit id: "first commit"
   commit id: "avance 1"
   branch feature/loop-engineering
   checkout feature/loop-engineering
   commit id: "agents: researcher + evaluator"
   commit id: "agents: refiner + sakana_fugu"
   commit id: "config: settings + domain_knowledge"
   commit id: "prompts: rhinitis ARIA 2020"
   commit id: "data: approved_drugs.json UTF-8"
   commit id: "dashboard: streamlit + plotly"
   commit id: "tests: loop + fugu + pipeline E2E"
   checkout main
   merge feature/loop-engineering id: "feat: loop engineering completo"
   commit id: "Add evaluation and research results"
```

---

## 🤝 Contribuir

Proyecto de investigación activa. PRs e issues bienvenidos, especialmente:
- Nuevas enfermedades objetivo con perfil Th2/inflamatorio
- Fármacos aprobados adicionales con evidencia inmunomoduladora
- Mejoras en los pesos del fitness multidimensional

---

<div align="center">

Hecho con 🧬 y Python async · Powered exclusively by [Qwen](https://huggingface.co/Qwen)

**Santiago de Chile · 2026**

</div>

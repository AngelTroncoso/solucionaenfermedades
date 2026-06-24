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

Pharma Loop Engineering combina **Loop Engineering** y un **agente evolutivo Sakana FuGU** para descubrir usos terapéuticos nuevos en fármacos ya aprobados por FDA/EMA. En lugar de sintetizar nuevas moléculas, mina perfiles farmacológicos existentes y evoluciona hipótesis hasta alcanzar plausibilidad clínica.

**Enfermedades objetivo prioritarias:**
- 🤧 Rinitis alérgica crónica (primaveral y al polvo) — pipeline especializado con criterios ARIA 2020
- Extensible a cualquier condición Th2-mediada o inflamatoria

> **Restricción de modelos:** toda la inferencia LLM corre exclusivamente en **modelos Qwen** vía OpenRouter. Sin GPT, Claude, Gemini ni Llama.

---

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart TD
    A([🚀 main.py]) --> B{Loop Engineering\nmax 10 iteraciones}

    B --> C[🔬 Researcher\nGenera hipótesis]
    C --> D[⚖️ Evaluator\nPuntúa 5 dimensiones]
    D --> E{fitness ≥ 0.80?}

    E -->|✅ Sí| F[(📁 research_results/\nHipótesis publicada)]
    E -->|❌ No| G[🔁 Refiner\nMejora iterativa]

    G --> H{¿Mejoró en\n3 rondas?}
    H -->|✅ Sí| D
    H -->|❌ No| I[🧬 Sakana FuGU\nEvolución por población]

    I --> J[Selección torneo\ntop 30%]
    J --> K[Crossover\nmecanismos moleculares]
    K --> L[Mutación\ndosis / vía / combinación]
    L --> C

    F --> M{¿Más enfermedades\nen cola?}
    M -->|✅ Sí| B
    M -->|❌ No| N([🏁 Fin])

    style A fill:#1e3a5f,color:#fff
    style F fill:#166534,color:#fff
    style I fill:#581c87,color:#fff
    style N fill:#1e3a5f,color:#fff
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
    agents
      researcher.py
      evaluator.py
      refiner.py
      sakana_fugu.py
    config
      settings.py
      domain_knowledge.yaml
      system_prompts
        researcher_system.md
        evaluator_system.md
        refiner_system.md
        rhinitis_specialist_system.md
    data
      drug_database
        approved_drugs.json
        evolution_memory.json
    dashboard
      results_viewer.py
    tests
      test_loop_engineering.py
      test_sakana_fugu.py
      test_rhinitis_pipeline.py
    research_results
    evaluation_results
    main.py
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
# Windows con Anaconda
C:\ProgramData\anaconda3\python.exe -m streamlit run dashboard/results_viewer.py

# Otros entornos
streamlit run dashboard/results_viewer.py
```

**Tests:**
```bash
pytest tests/ -v --asyncio-mode=auto
```

---

## ⚙️ Configuración

```python
# config/settings.py
MODEL_REASONING   = "qwen/qwen3-235b-a22b"       # hipótesis profundas
MODEL_FAST        = "qwen/qwen2.5-72b-instruct"   # evaluación y refinement
MODEL_LIGHT       = "qwen/qwen2.5-7b-instruct"    # tareas simples
MAX_ITERATIONS    = 10
FITNESS_THRESHOLD = 0.80
POPULATION_SIZE   = 10
MUTATION_RATE     = 0.30
EARLY_STOP_ROUNDS = 3
```

```env
# .env
OPENROUTER_API_KEY=your_key_here
MODEL_REASONING=qwen/qwen3-235b-a22b
MODEL_FAST=qwen/qwen2.5-72b-instruct
FITNESS_THRESHOLD=0.80
MAX_ITERATIONS=10
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

## 🔬 Sakana FuGU — Agente Evolutivo

```mermaid
flowchart LR
    A[🌱 Población inicial\nN hipótesis] --> B[📊 Evaluar fitness\n5 dimensiones]
    B --> C{fitness ≥ 0.80?}
    C -->|✅| D[(💾 Publicar\nhipótesis)]
    C -->|❌| E[🏆 Selección torneo\ntop 30%]
    E --> F[🔀 Crossover\nmecanismos padre]
    F --> G[🎲 Mutación\ndosis / vía / combinación]
    G --> H{¿Convergió?}
    H -->|❌| B
    H -->|✅| I([🏁 Mejor hipótesis])

    style D fill:#166534,color:#fff
    style I fill:#1e3a5f,color:#fff
```

Checkpoints guardados cada 3 generaciones en `data/drug_database/evolution_memory.json`.

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

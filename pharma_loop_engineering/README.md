# Pharma Loop Engineering

AI-powered pharmaceutical drug discovery framework using multi-agent systems.

## Overview

Pharma Loop Engineering is a comprehensive framework for automating and enhancing drug discovery workflows using AI agents, advanced computational models, and intelligent automation.

## Project Structure

```
pharma_loop_engineering/
├── agents/               # AI agents for different phases
│   ├── orchestrator.py   # Central workflow coordinator
│   ├── researcher.py     # Literature & data gathering
│   ├── designer.py       # Molecular design
│   ├── implementer.py    # Model implementation
│   ├── evaluator.py      # Results evaluation
│   └── refiner.py        # Iterative optimization
├── skills/               # Reusable capabilities
│   ├── research_skill.py           # Literature search
│   ├── design_skill.py             # Molecular design
│   ├── code_generation_skill.py    # Code generation
│   ├── analysis_skill.py           # Data analysis
│   ├── visualization_skill.py      # Visualization
│   └── optimization_skill.py       # Optimization
├── plugins/              # External integrations
│   ├── llm_plugin.py              # LLM providers
│   ├── database_plugin.py         # Database connectors
│   ├── pubmed_plugin.py           # PubMed API
│   ├── chembl_plugin.py           # ChEMBL API
│   └── visualization_plugin.py    # Visualization tools
├── dashboard/            # Streamlit dashboard
│   ├── app.py                      # Main app
│   ├── components/                 # UI components
│   └── assets/                     # Static assets
├── worktrees/            # Experiment management
│   └── state_manager.py            # State tracking
├── config/               # Configuration
│   ├── settings.yaml               # Main config
│   ├── prompts.yaml                # LLM prompts
│   └── settings.py                 # Config loader
├── data/                 # Data storage
│   ├── drug_database/              # SQLite database
│   └── results/                    # Workflow results
├── notebooks/            # Jupyter notebooks
├── tests/                # Unit tests
├── requirements.txt      # Dependencies
├── .env.example          # Environment variables
├── .gitignore
├── main.py               # Entry point
└── README.md

## Features

- Multi-agent workflow orchestration
- Literature search (PubMed, ChEMBL)
- Molecular design and optimization
- Predictive modeling (QSAR, docking)
- Interactive dashboard
- Experiment tracking with worktrees
- LLM-powered code generation

## Installation

```bash
# Clone repository
git clone <repository-url>
cd pharma_loop_engineering

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

1. Copy `.env.example` to `.env` and add your API keys
2. Modify `config/settings.yaml` for your needs
3. Adjust `config/prompts.yaml` for domain-specific tasks

## Usage

### Run workflow
```bash
python main.py run
```

### Launch dashboard
```bash
python main.py dashboard
# Or: streamlit run dashboard/app.py
```

### Check status
```bash
python main.py status
```

## Development

### Run tests
```bash
pytest tests/
```

### Add new agent
1. Create `agents/new_agent.py`
2. Implement required interface
3. Register in `main.py`

### Add new skill
1. Create `skills/new_skill.py`
2. Implement capability methods
3. Update agents to use the skill

## Architecture

### Agents
- **Orchestrator**: Coordinates workflow phases
- **Researcher**: Searches literature and databases
- **Designer**: Generates and optimizes molecules
- **Implementer**: Builds computational models
- **Evaluator**: Assesses results and metrics
- **Refiner**: Iteratively improves candidates

### Skills
Reusable capabilities that agents can use:
- Research, design, analysis, visualization, optimization, code generation

### Plugins
External service integrations:
- LLMs, databases, PubMed, ChEMBL, visualization tools

## Contributing

Contributions welcome! Please submit PRs with clear descriptions.

## License

MIT License

## Contact

For questions or support, please open an issue.
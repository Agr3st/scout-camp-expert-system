# Scout Camp Guardian 🏕️

Fuzzy Logic Multilevel Expert System for Scout Camp Safety

## 📌 Project Overview

**Scout Camp Guardian** is a modular expert system based on **fuzzy logic**, designed to support decision-making, coordination, and safety management in scout camps.

The system evaluates multiple aspects influencing camp safety — such as **weather conditions**, **organizational readiness**, and **terrain** — and integrates them into a **multi-level fuzzy inference architecture**.  
Each module produces an interpretable risk assessment, which is then combined into a higher-level evaluation of the **overall camp risk**.

The application provides camp leaders with **clear, human-readable risk levels** (e.g. low / medium / high), supporting timely and informed operational decisions, especially under uncertain and dynamic conditions.

This project is developed as part of my **engineering thesis** at  
**AGH University of Science and Technology (Data Science)**.

---

## Key Features

- ✅ **Multi-level fuzzy expert system** (hierarchical risk assessment).  
- ✅ **Weather-based risk analysis** using real-time forecast data (Open-Meteo API).  
- ✅ **Organizational and infrastructure risk modules** (personnel experience, terrain, evacuation conditions).  
- ✅ **Human-interpretable linguistic variables** (e.g. *strong wind*, *high risk*).  
- ✅ **Automated data orchestration and session-based state management**.  
- ✅ **Interactive desktop prototype built with Streamlit**.  

## Installation

### Clone the repository

```git
git clone https://github.com/Agr3st/scout-camp-expert-system.git
```

```bash
cd scout-camp-expert-system
```

### Create and activate virtual environment

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

### Install requirements

```bash
pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

## Running the application

From the project root directory:

```bash
export PYTHONPATH=$(pwd)
```

```bash
streamlit run app.py
```

### On Windows

```powershell
$env:PYTHONPATH = (Get-Location)
```

```powershell
streamlit run app.py
```

## Project structure

```md
scout-camp-expert-system/
├── src/
│ ├── fuzzy/
│ │ ├── base.py             # Base classes for fuzzy logic modules
│ │ ├── weather.py          # Weather risk module
│ │ ├── organization.py     # Organization risk module
│ │ ├── terrain.py          # Terrain risk module
│ │ ├── camp.py             # High-level camp risk module
│ │ └── visualizations.py   # Fuzzy visualizations
│ │
│ ├── orchestrators/
│ │ ├── weather_orchestrator.py         # Weather data → fuzzy weather risk pipeline
│ │ ├── organization_orchestrator.py    # Organization input → organization risk
│ │ ├── terrain_orchestrator.py         # Terrain → vulnerability
│ │ └── camp_orchestrator.py            # Aggregates all risks into camp risk
│ │
│ ├── scraper/
│ │ └── open_meteo.py  # Open-Meteo API client and weather data parsing
│ │
│ ├── ui/
│ │ ├── cockpit.py              # Main dashboard view (1. and 2. level results)
│ │ ├── weather_module.py       # Weather module UI
│ │ ├── organization_module.py  # Organization module UI
│ │ ├── terrain_module.py       # Terrain module UI
│ │ ├── input.py                # User input forms (location, organization data, etc.)
│ │ ├── session_data.py         # Debug view of Streamlit session state
│ │ └── info.py                 # About / documentation page
│ │
│ ├── utils/
│ │ ├── config.py  # Config loading (YAML)
│ │ ├── logger.py  # Centralized logging setup
│ │ ├── session.py # Streamlit session_state initialization
│ │ └── ui.py      # Reusable UI components (chips, rows, etc.)
│ │
│ │
│ ├── app.py # Streamlit app entry point
│ └── init.py
│
├── config.yaml      # Global configuration (colors, logging, rules)
├── README.md        # Project documentation
└── requirements.txt # Python dependencies
```

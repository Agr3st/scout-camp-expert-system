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

## System Architecture

The **Scout Camp Guardian** system is designed as a **multi-level, modular expert system** based on fuzzy logic.  
Its architecture follows the principle of **separation of concerns**, enabling scalability, reusability, and independent development of individual decision modules.

The system is composed of three main layers:

---

### 1️⃣ Data Acquisition Layer

This layer is responsible for collecting and preparing raw input data required by the expert system.

- Weather data is retrieved from the **Open-Meteo API** using a dedicated scraper module.
- Forecast data is processed into structured pandas DataFrames with proper timezone handling.
- User-defined inputs (e.g. camp location, organizational parameters) are collected via the Streamlit UI.
- All acquired data is stored in the **Streamlit session state**, ensuring consistency across application views.

📁 *Key components*:
- `scraper/open_meteo.py`
- `utils/session.py`
- `ui/input.py`

---

### 2️⃣ Fuzzy Inference Layer

The core decision-making logic is implemented in this layer.  
It consists of **independent fuzzy logic modules**, each responsible for evaluating a specific aspect of camp safety.

#### First-Level Modules

These modules operate on raw or lightly processed input data and generate interpretable risk indicators:

- **Weather Module**  
  Assesses weather-related risk based on variables such as temperature, wind, precipitation, and thunderstorm conditions.

- **Organizational Module**  
  Evaluates organizational risk using parameters such as number of participants and staff experience.

- **Terrain Module**  
  Estimates camp vulnerability based on terrain difficulty and evacuation conditions.

Each module outputs a **linguistic and numerical risk value** (e.g. *low*, *medium*, *high*).

📁 *Key components*:
- `fuzzy/weather.py`
- `fuzzy/organization.py`
- `fuzzy/terrain.py`
- `fuzzy/base.py`

---

### 3️⃣ High-Level Aggregation Layer

At the highest level, outputs from first-level modules are combined into a **global camp risk assessment**.

- The **Camp Risk Module** receives fuzzy outputs from subordinate modules.
- It performs a second-stage fuzzy inference to determine the **overall camp safety status**.
- This hierarchical approach allows the system to model complex dependencies and uncertainty propagation.

📁 *Key components*:
- `fuzzy/camp.py`
- `orchestrators/camp_orchestrator.py`

---

### 4️⃣ Orchestration and State Management

The system uses dedicated **orchestrator modules** to manage execution flow:

- Triggering data refresh cycles (e.g. weather updates).
- Executing fuzzy inference pipelines.
- Updating shared application state.

📁 *Key components*:
- `orchestrators/weather_orchestrator.py`
- `orchestrators/organization_orchestrator.py`
- `orchestrators/terrain_orchestrator.py`

---

### 5️⃣ Presentation Layer

The user interface is implemented using **Streamlit** and provides:

- Real-time visualization of module inputs and outputs.
- Human-readable linguistic interpretations.
- Time-series risk charts.
- Diagnostic views (session data).

📁 *Key components*:
- `ui/weather_module.py`
- `ui/organization_module.py`
- `ui/terrain_module.py`
- `ui/cockpit.py`
- `ui/session_data.py`

---

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
│ └── app.py # Streamlit app entry point
│
├── config.yaml      # Global configuration (colors, logging, rules)
├── README.md        # Project documentation
└── requirements.txt # Python dependencies
```

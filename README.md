# Scout Camp Guardian 🏕️

Fuzzy Logic Multilevel Expert System for Scout Camp Safety

## 📌 Project Overview

**Scout Camp Guardian** is an expert system based on fuzzy logic, designed to support the coordination and safety management of scout camps.  
The system continuously monitors weather conditions and evaluates potential threats to camp safety. Based on fuzzy inference, it generates **risk levels** for camp staff.

This project is part of my engineering thesis at **AGH University of Science and Technology (Data Science)**.

---

## Features

- ✅ Real-time weather data monitoring via API (OpenWeatherMap/IMGW).  
- ✅ Fuzzy logic-based risk assessment (low / medium / high).  
- ✅ Simple desktop prototype (Streamlit).  

## Installation

### Clone the repository

```git
git clone https://github.com/Agr3st/scout-camp-expert-system.git

```bash
cd scout-camp-expert-system
```

### Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the application

From the project root directory:

```bash
export PYTHONPATH=$(pwd)
streamlit run src/app.py
```

### On Windows

```powershell
$env:PYTHONPATH = (Get-Location)
streamlit run src/app.py
```

## Project structure

```
scout-camp-expert-system/
├── src/
│   ├── fuzzy/
│   │   ├── visualizations.py      # Fuzzy logic visualization utilities (membership functions, inference plots)
│   │   └── weather.py             # Weather fuzzy logic system (variables, rules, risk assessment)
│   │
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── open_meteo.py          # Open-Meteo API client and weather forecast data parsing
│   │
│   ├── ui/
│   │   ├── cockpit.py             # Main dashboard (system overview)
│   │   ├── info.py                # Application information and documentation page
│   │   ├── input.py               # User input page (location, module configuration)
│   │   ├── session_data.py        # Debug/inspection view of Streamlit session_state
│   │   └── weather_module.py      # Weather module UI (risk display, charts, inputs)
│   │
│   ├── utils/
│   │   ├── config.py              # Configuration loading utilities (YAML, paths)
│   │   ├── logger.py              # Centralized application logging setup
│   │   ├── session.py             # Streamlit session_state initialization and helpers
│   │   ├── ui.py                  # Reusable UI components (chips, rows, widgets)
│   │   └── weather_orchestrator.py# Weather module orchestration and helpers
│   │
│   ├── __init__.py
│   └── app.py                     # Streamlit application entry point and navigation
│
├── config.yaml                    # Global application configuration
├── README.md                      # Project documentation and setup instructions
└── requirements.txt               # Python dependencies
```
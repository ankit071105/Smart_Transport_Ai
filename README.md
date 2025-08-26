# Smart AI Public Transport & Route Optimizer 🚌

An AI-powered public transport companion that helps commuters find the **fastest**, **least crowded**, and **safest** routes using advanced machine learning and real-time data analysis.

<p align="center">
  <a href="https://python.org"><img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue.svg"></a>
  <a href="#"><img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-UI-red"></a>
  <a href="#"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ML-orange"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/badge/License-MIT-green"></a>
</p>

---

## 🌟 Features

- **Smart Route Recommendation** – AI-powered suggestions based on real-time traffic and crowd density.  
- **Multi-modal Transport** – Buses, trains, walking, and combinations.  
- **Real-time Tracking** – Live progress with proactive alerts and dynamic re-routing.  
- **Voice Guidance** – Text-to-speech turn-by-turn instructions; accessibility-friendly.  
- **Travel History** – Review past journeys and patterns with interactive charts.  
- **Customizable Preferences** – Prioritize fastest, safest, or least crowded routes.  
- **SOS Emergency** – Quick access to emergency contacts from within the app.

---

## 🛠️ Tech Stack & Architecture

**Frontend & UI**
- **Streamlit**: Python-based web UI framework for fast, interactive dashboards.

**Backend & Data Processing**
- **Python** (3.10+) as core language
- **PyTorch**: LSTM-based time-series prediction
- **NumPy / Pandas**: data wrangling & feature engineering

**Mapping & Geospatial**
- **OpenRouteService API**: routing, directions, and geocoding  
- **Folium**: map visualization (Leaflet.js wrapper)  
- **Geopy**: geocoding utilities (fallbacks like Nominatim)

**Database**
- **SQLite**: local storage for users, travel history, predictions

**Voice & Audio**
- **gTTS**: text-to-speech
- **PyGame**: audio playback

**Additional**
- **Plotly**: interactive charts
- **streamlit-option-menu**: enhanced navigation
- **Requests**: HTTP client

### System Flow


1. Clone the repository:
```bash
smart-transport-ai/
├─ app.py # Streamlit entry point
├─ requirements.txt
├─ README.md
├─ .env.example # Example environment variables
├─ assets/
│ ├─ logo.png
│ └─ styles.css # optional custom styles
├─ config/
│ └─ settings.py # app constants, thresholds
├─ core/
│ ├─ preferences.py # user preference management
│ ├─ alerts.py # congestion/safety alert logic
│ ├─ tracking.py # progress simulation + live updates
│ └─ utils.py # common helpers
├─ database/
│ ├─ database.py # CRUD ops
│ └─ schema.sql # schema (optional)
├─ ml/
│ ├─ dataset.py # time-series dataset
│ ├─ model.py # LSTM model definition
│ ├─ train.py # training script
│ └─ inference.py # prediction utilities
├─ routing/
│ ├─ map_utils.py # ORS integration, polyline, folium maps
│ └─ route_agent.py # scoring/selection pipeline
└─ ui/
├─ pages/ # Streamlit multipage views
│ ├─ 1_🚏_Plan_a_Route.py
│ ├─ 2_📍_Live_Tracking.py
│ ├─ 3_📊_History_&Insights.py
│ └─ 4⚙️_Settings.py
└─ components.py # reusable UI widgets
```


```bash
# 1) Clone the repository
git clone https://github.com/yourusername/Smart_Transport_Ai.git
cd Smart_Transport_Ai

# 2) (Recommended) create a virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Initialize the database
python -c "from database.database import init_db; init_db()"

# 5) Run the application
streamlit run app.py
```

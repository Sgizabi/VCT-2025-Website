# 🎯 VCT 2025 Intel Hub

A full-season Valorant Champions Tour analytics dashboard built with Streamlit and Plotly.
Covers **15 events**, **4 regions**, **50+ teams**, and **324 players**.

---
# Live Demo

link: https://vct-2025-website.streamlit.app

---

## Data Source
Data sourced from ["Valorant 2025 - All Events International + Regional"](https://www.kaggle.com/datasets/piyush86kumar/valorant-vct-2025-all-events)
by Piyush Kumar on Kaggle, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Originally collected from [vlr.gg](https://www.vlr.gg).

---

## Quick Start

### 1. Install dependencies
```bash
pip install streamlit plotly pandas numpy
```

### 2. Set up your data
Place the `VCT_2025_data` zip (or extracted folder) in the same directory as `app.py`, then run:
```bash
python setup_data.py
```
This creates a `VCT_data/` folder the app reads from.

### 3. Run the app
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

---

## Folder Structure
```
app.py
setup_data.py
VCT_data/
├── VCT 2025 Americas Kickoff_csvs/
├── VCT 2025 Americas Stage 1_csvs/
├── ... (15 event folders total)
└── columns_description.csv
```

---

## What's Inside — 8 Tabs

| Tab | What it shows |
|---|---|
| 🔬 **Overview** | Interactive team bubble chart + top-5 per metric |
| 👤 **Player Scouting** | Scatter by role, full stats table, head-to-head radar |
| 📈 **Season Arcs** | ACS trajectory across events, arc classification (Rocket Ship, Burnout, etc.), and a Player Evolution Gallery showing radar snapshots per event |
| 🛡️ **Team Analysis** | Style radar, economy deep-dive (eco/pistol/full-buy), report card heatmap |
| 🗺️ **Map Mastery** | Attack/defense bias, team map pool radar, pick rates |
| 💥 **Clutch & Pressure** | Big Game Hunters scatter (rounds-weighted), pressure gauge (win rates not raw counts), multi-kill/clutch stars |
| 🎯 **Agent Meta** | Pick rates, agent×map heatmap, role balance by region |
| 📊 **Report Card** | Full sortable leaderboard + season leaders per category |

---

## Sidebar Filters
All tabs respond to three global filters in the sidebar:
- **Region** — Americas / EMEA / Pacific / China / All
- **Event** — Any of the 15 individual events, or All
- **Min Rounds** — Filter out low-sample players

---

## Methodology Notes
A few analytical choices worth knowing about if you're presenting this project:
- **Role assignment** uses a 65% dominance threshold on agents played per role (from per-map performance data) — a player below that threshold on any single role is labeled "Flex."
- **Season arc classification** fits a degree-2 polynomial against calendar dates (not just event order), and reports R² alongside each player's arc type so low-confidence trajectories can be filtered out.
- **Big Game Hunter** comparisons use rounds-weighted averages, so a player's rating isn't skewed by one short series.
- **Pressure Gauge** uses win *rates* (wins ÷ matches at that stake level), not raw win counts, so heavily-played teams don't get an unfair advantage.

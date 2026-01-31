# Toronto Housing Inflation Analysis (2015–2025)

##  Project Overview
This project analyzes **Toronto MLS Home Price Index (HPI) benchmark housing prices** from **January 2015 through 2025**, using data published by the **Toronto Regional Real Estate Board (TRREB)**.

The original MLS benchmark dataset can be accessed here:  
[TRREB – MLS Home Price Index](https://trreb.ca/market-data/mls-home-price-index/)

The analysis focuses on housing inflation dynamics driven by:
- COVID-19 demand shocks (2020–2022)
- Structural housing supply constraints
- Post-peak correction and market stabilization (2023–2025)

Rather than treating housing prices as a single trend, this project decomposes inflation across **property types**, **regions**, and **time periods**, highlighting where inflation concentrated and where volatility increased heavily.

##  Live Dashboard
Access the full interactive dashboard here:

https://toronto-housing-inflation-dashboard.onrender.com/

##  Repository Contents
- `app.py` – Shiny for Python dashboard application  
- `Toronto 2015-2025 - MLS_Google_MLS_FULL.csv` – MLS benchmark housing dataset  
- `location_coords.csv` – Latitude/longitude mapping for Toronto regions  
- `static/` – Images, UI assets, and custom styling  

##  Tools & Technologies
- **Python** – End-to-end data analysis and application logic  
- **Pandas** – Time-series aggregation, inflation calculations, segmentation  
- **Plotly** – Interactive pie and bar charts with real-time filtering  
- **IPyLeaflet** – Geographic benchmark price visualization by region  
- **Shiny for Python** – Reactive UI and dashboard framework  

## Dashboard Screenshots

### Full Dashboard Overview
![Dashboard Overview](<img width="1920" height="946" alt="Dashboard Overview 1" src="https://github.com/user-attachments/assets/2080f3c4-50d8-4d22-9f9e-d39beb69bd38" />
)

This view establishes the **scope and credibility** of the analysis.

Key metrics shown:
- **Total benchmark records:** ~9,900+ monthly observations  
- **Geographic regions:** 170+ Toronto MLS locations  
- **Property types:** 5 standardized housing categories  
- **Time coverage:** 125+ monthly periods (2015–2025)  

Because MLS HPI methodology controls for housing composition, the data reflects **true price inflation**, not changes in transaction mix.

### Property Type Distribution & Inflation Pressure
![Pie Charts](pie_charts.png)

These charts use **2025 benchmark prices** to quantify how cumulative inflation reshaped the housing market.

- **Average benchmark prices (2025):**  
  - Detached: ~$1.42M  
  - Semi-Detached: ~$1.03M  
  - Composite: ~$1.04M  
  - Townhouse: ~$776K  
  - Apartment: ~$586K  

- **Total market value concentration:**  
  Detached and Semi-Detached properties account for the majority of total market value despite lower unit counts, indicating capital concentration rather than housing availability.

- **Price spread (max − min across regions):**  
  - Detached homes exhibit the largest spread (>$1M)  
  - Apartments show the tightest spread, indicating lower volatility  

### Regional & Temporal Inflation Patterns
![Bar Charts](bar_charts.png)

These visualizations analyze **regional inequality and time-based inflation dynamics**.

- Detached housing dominates price leadership in all top regions  
- All regions show synchronized acceleration beginning in 2020  
- Composite benchmarks peak in 2022, followed by partial correction  
- No region returns to pre-COVID price levels by 2025  

##  Key Analytical Findings

- **Dataset scope:**  
  - Time range: 2015–2025  
  - Frequency: Monthly MLS benchmarks  
  - Regions: 170+ Toronto neighborhoods  
  - Property types: Composite, Detached, Semi-Detached, Townhouse, Apartment  

- **Long-run inflation (2015 → 2025):**  
  - Detached: **+95.7%**  
  - Semi-Detached: **+82.7%**  
  - Composite: **+79.1%**  
  - Townhouse: **+79.0%**  
  - Apartment: **+73.4%**  

- **COVID-era inflation shock (2019 → 2022):**  
  - Detached: **+66.5%**  
  - Semi-Detached: **+61.7%**  
  - Composite: **+53.0%**  
  - Townhouse: **+49.1%**  
  - Apartment: **+39.0%**  

- **Volatility & risk:**  
  Detached housing shows the greatest price volatility and correction risk, while apartments demonstrate lower volatility but persistent inflation pressure.

- **Post-peak adjustment (2023 → 2025):**  
  Market cooling occurred across all segments, but inflation permanently reset price baselines.

- **Geographic inequality:**  
  Central regions dominate top price rankings, while peripheral regions follow similar inflation trajectories at lower absolute price levels.

##  How to Use This Project
1. Clone the repository  
2. Install dependencies  
3. Run `app.py`  
4. Use the interactive charts and map to explore inflation by year, region, and property type  

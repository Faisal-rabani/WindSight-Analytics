<div align="center">

<img src="docs/assets/logo.svg" alt="WindSight Analytics Logo" width="100%" max-width="820" />

<br />

# UK Wind Power Forecast Intelligence Platform
### Enterprise Decision-Time Analytics for Day-Ahead Power Procurement Desk

[![Live Production App](https://img.shields.io/badge/Production%20App-Live%20on%20Vercel-10B981?style=for-the-badge&logo=vercel&logoColor=white)](https://wind-sight-analytics-69qp.vercel.app/)
[![Live REST API](https://img.shields.io/badge/REST%20API-Online%20(200%20OK)-0284C7?style=for-the-badge&logo=fastapi&logoColor=white)](https://wind-sight-analytics.vercel.app/api/v1/health)
[![Elexon BMRS Verified](https://img.shields.io/badge/Data%20Source-Official%20Elexon%20BMRS-0D9488?style=for-the-badge&logo=databricks&logoColor=white)](https://data.elexon.co.uk/bmrs/api/v1)

<br />

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18.3.1-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Automated Tests](https://img.shields.io/badge/Pytest-18%2F18%20Passing%20(100%25)-22C55E?style=flat-square&logo=pytest&logoColor=white)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-EAB308?style=flat-square)](LICENSE)

<br />

---

### 🖥️ Live Production Dashboard Preview

<a href="https://wind-sight-analytics-69qp.vercel.app/" target="_blank">
  <img src="docs/assets/dashboard-preview.png" alt="WindSight Analytics Executive Dashboard" width="880" style="border-radius: 12px; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5); border: 1px solid #1e293b;" />
</a>

<p align="center">
  <b><a href="https://wind-sight-analytics-69qp.vercel.app/">🚀 Launch Live Web Application</a></b> &nbsp;•&nbsp; 
  <b><a href="https://wind-sight-analytics.vercel.app/api/v1/health">📡 Live Health API</a></b> &nbsp;•&nbsp; 
  <b><a href="docs/demo-script.md">🎬 10-Minute Video Script</a></b>
</p>

</div>

---

## 1. Executive Summary & Business Objective

In the UK wholesale power market, utilities purchase electricity on a **Day-Ahead ($D - 1$)** basis to satisfy customer demand. Wind electricity generation is weather-dependent and volatile:

- **Overforecasting Wind (Under-procurement)**: Leads to dangerous short positions in real-time settlement, exposing the utility to severe National Grid ESO balancing mechanism cashout charges.
- **Underforecasting Wind (Over-procurement)**: Forces long positions where surplus energy must be spilled or sold back at heavily depressed imbalance prices.
- **The "Hindsight Bias" Trap**: Standard analytical tools evaluate forecasts published *hours before delivery*. In practice, day-ahead wholesale trades must be finalized by the **10:00 AM UK Local Time ($D - 1$) Cutoff**. Evaluating post-cutoff forecasts introduces false hindsight confidence.

The **UK Wind Power Forecast Intelligence Platform** is purpose-built for energy procurement teams to evaluate the exact generation forecasts that were physically available at decision commitment time, benchmark them against delivered physical actuals, quantify forecast risks (MAE, RMSE, Bias), and detect extreme volatility events throughout **January 2026**.

---

## 2. January 2026 Verified Analytics

All metrics are quantitatively calculated from official, un-interpolated **Elexon BMRS** datasets for the evaluation period (1–31 January 2026):

| Metric | Verified Value | Benchmark Description | Commercial Risk Implication |
| :--- | :---: | :--- | :--- |
| **Mean Absolute Error (MAE)** | **2,107.18 MW** | Average deviation between committed forecast and actual output | Baseline volume uncertainty per procurement period |
| **Root Mean Square Error (RMSE)** | **2,611.24 MW** | Quadratic error penalizing extreme volatility misses | Highlights volatile spikes requiring expensive peaking reserves |
| **Mean Bias Error (MBE)** | **+1,839.92 MW** | Systematic directionality ($\text{Forecast} - \text{Actual}$) | **Severe persistent overforecasting**: Utility is systematically under-procured |
| **Maximum Single Miss** | **+6,857.00 MW** | Peak error recorded on **12 Jan 2026 01:00 UTC** | Catastrophic volume miss (Forecast: 20,905 MW vs Actual: 14,048 MW) |
| **Decision Coverage** | **50.0%** (744 / 1,488) | Exactly matched hourly intervals across all 48 settlement periods | Honest representation without synthetic data fabrication |
| **Mean Delivered Actuals** | **11,581.11 MW** | Physical January 2026 wind generation delivered | Actual wind output benchmark |

> [!WARNING]
> **Procurement Risk Takeaway**: With an average bias of **+1,840 MW** and peak misses exceeding **6.8 GW**, relying naively on day-ahead wind forecasts without bias-correction algorithms forces the utility desk into costly system balancing penalties on over 75% of January days.

---

## 3. Decision-Time Matching Architecture

To prevent hindsight bias, the engine enforces strict temporal filtering based on the procurement desk's operational cutoff:

```mermaid
flowchart TD
    A[Elexon BMRS Stream] -->|WINDFOR API| B[(Forecast Publications Repository)]
    A -->|FUELHH WIND API| C[(Delivered Actuals Repository)]
    
    D[Delivery Day D] --> E{Decision Cutoff Rule}
    E -->|10:00 AM UK Local Time on D-1| F[Cutoff Timestamp UTC]
    
    B --> G[Temporal Filter Engine]
    F --> G
    
    G -->|Condition: publishTime <= Cutoff UTC| H[Eligible Day-Ahead Forecasts]
    G -->|Condition: publishTime > Cutoff UTC| I[REJECTED: Hindsight Violation]
    
    H --> J[Select Latest Forecast: max publishTime]
    J --> K[Matching Engine]
    C --> K
    
    K --> L[Matched Interval Records]
    L --> M[Statistical Analytics Engine: MAE, RMSE, Bias]
    L --> N[React Executive UI & Charts]
```

### Core Matching Algorithm
1. **Decision Deadline**: For target delivery day $D$, the decision commitment cutoff is **10:00 AM UK Local Time (`Europe/London`) on $D - 1$**.
2. **Timezone Awareness**: The local 10:00 AM timestamp is converted to UTC via Python `zoneinfo` (e.g. `2025-12-31 10:00:00 UTC` for `2026-01-01` deliveries).
3. **Strict Eligibility**: A forecast targeting settlement interval $T$ is eligible if and only if:
   $$\text{publishTime} \le \text{cutoff}_{\text{UTC}}$$
4. **Latest Available Selection**:
   $$\text{Selected Forecast} = \arg\max_{\text{eligible}} (\text{publishTime})$$
5. **No Synthetic Manipulation**: Half-hourly settlement periods that do not have an hourly forecast published prior to cutoff are flagged as missing, maintaining 100% audit integrity.

---

## 4. Platform Features & Pages

The application is structured into four specialized workflows designed for energy analysts and procurement traders:

<div align="center">

| Page | Primary Purpose | Key Visual Components |
| :--- | :--- | :--- |
| **1. Executive Overview** | High-level summary of January 2026 KPIs and market impact | MAE/RMSE/Bias KPI cards, full-month interactive Recharts timeline, quick date-range filter tabs, extreme misses preview |
| **2. Wind Forecasts** | Operational forecast vs actual comparison table | Paginated settlement table (744 records), direction tags (over/underforecast), forecast age indicators, search and date filtering |
| **3. Accuracy Analysis** | Deep-dive statistical and volatility assessment | Daily MAE/RMSE trend bar charts, error distribution histogram, 15 largest volatility miss intervals |
| **4. Methodology** | Transparent operational and mathematical documentation | Exact mathematical formulas, timezone conversion rules, official Elexon schema definitions, architectural trade-offs |

</div>

---

## 5. Technology Stack & Design System

The system is engineered as an enterprise-grade monorepo with clean micro-architectural boundaries:

```
WindSight-Analytics/
├── frontend/                     # Modern React 18 SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── app/                  # Application root, router, React Query client
│   │   ├── components/           # Reusable KPI cards, Recharts visualizations, layout
│   │   ├── hooks/                # Custom React Query hooks (useOverview, useForecasts, useAccuracy)
│   │   ├── pages/                # OverviewPage, ForecastPage, AccuracyPage, MethodologyPage
│   │   ├── services/             # Axios API client with error interceptors
│   │   └── types/                # Strict TypeScript domain interfaces
│   ├── vercel.json               # SPA client-side routing configuration
│   └── package.json
├── backend/                      # Production Flask Python Backend
│   ├── app/
│   │   ├── analytics/            # Decision logic, metrics (MAE, RMSE, MBE), aggregations
│   │   ├── api/routes/           # REST blueprints (/health, /analytics, /forecasts, /actuals)
│   │   ├── models/               # SQLAlchemy ORM models (ActualGeneration, WindForecast)
│   │   ├── repositories/         # Storage abstraction (ActualRepository, ForecastRepository)
│   │   ├── services/             # MatchingService (memoized cache), ElexonClient, AnalyticsService
│   │   └── utils/                # Timezone converters, input validators, structured logger
│   ├── api/index.py              # Vercel Serverless Function entry point
│   ├── data/                     # Bundled SQLite database (wind_forecast.db)
│   ├── tests/                    # Pytest test suite (18 automated tests)
│   ├── vercel.json               # Serverless rewrite and routing configuration
│   └── wsgi.py                   # Production WSGI entry point
├── docs/                         # System Documentation & Assets
│   ├── assets/                   # Vector logo, high-res dashboard preview
│   ├── architecture.md           # Full system architecture documentation
│   ├── methodology.md            # Detailed mathematical and trading methodology
│   └── demo-script.md            # 10-minute presentation and video demonstration script
└── docker-compose.yml            # Multi-container orchestration (Nginx + Python Gunicorn)
```

---

## 6. Official Elexon BMRS Datasets

Only official Elexon BMRS endpoints are utilized:

1. **Actual Wind Generation (`FUELHH/stream`)**:
   - Endpoint: `https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream`
   - Filter: `fuelType = 'WIND'`
   - Resolution: 30-minute settlement periods (48 periods/day)
   - Ingested: **1,584 physical generation records** (1 Jan 2026 to 2 Feb 2026)

2. **Forecast Wind Generation (`WINDFOR/stream`)**:
   - Endpoint: `https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream`
   - Fields: `startTime`, `publishTime`, `generation` (MW)
   - Resolution: Hourly forecasts with up to 48-hour forward horizon
   - Ingested: **19,856 forecast publications** (30 Dec 2025 to 2 Feb 2026)

---

## 7. Quickstart & Local Setup

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** & npm
- *(Optional)* **Docker & Docker Compose**

### Option A: Standard Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Faisal-rabani/WindSight-Analytics.git
   cd WindSight-Analytics
   ```

2. **Backend Setup (Python Flask):**
   ```bash
   cd backend
   python -m venv .venv
   
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   python wsgi.py
   ```
   *Backend starts on `http://127.0.0.1:5000` (pre-bundled with January 2026 SQLite database).*

3. **Frontend Setup (React + Vite):**
   ```bash
   cd ../frontend
   npm install
   npm run dev -- --port 3000
   ```
   *Access the web application at `http://localhost:3000`.*

---

### Option B: Docker Containerized Setup

To build and run both frontend (Nginx) and backend (Gunicorn) with a single command:
```bash
docker compose up --build
```
- **Web App**: `http://localhost:3000`
- **REST API**: `http://localhost:5000/api/v1/health`

---

## 8. Automated Testing Suite

The platform includes an automated testing suite verifying all mathematical calculations, decision cutoffs, boundary days, and API contracts.

```bash
cd backend
pytest -v
```

### Verified Test Results:
```text
tests/test_api.py::test_health_endpoint PASSED                           [  5%]
tests/test_api.py::test_overview_endpoint PASSED                         [ 11%]
tests/test_api.py::test_forecast_comparison_endpoint PASSED              [ 16%]
tests/test_api.py::test_invalid_date_validation PASSED                   [ 22%]
tests/test_decision_logic.py::test_decision_cutoff_calculation PASSED    [ 27%]
tests/test_decision_logic.py::test_boundary_january_1_purchasing_decision PASSED [ 33%]
tests/test_decision_logic.py::test_boundary_january_31_decision_february_1_delivery PASSED [ 38%]
tests/test_decision_logic.py::test_forecast_eligibility PASSED           [ 44%]
tests/test_decision_logic.py::test_select_best_eligible_forecast PASSED  [ 50%]
tests/test_decision_logic.py::test_no_eligible_forecast_returns_none PASSED [ 55%]
tests/test_matching.py::test_matching_exact_interval_and_cutoff PASSED   [ 61%]
tests/test_matching.py::test_idempotent_duplicate_handling PASSED        [ 66%]
tests/test_metrics.py::test_calculate_forecast_error PASSED              [ 72%]
tests/test_metrics.py::test_calculate_mae PASSED                         [ 77%]
tests/test_metrics.py::test_calculate_rmse PASSED                        [ 83%]
tests/test_metrics.py::test_calculate_bias PASSED                        [ 88%]
tests/test_metrics.py::test_compute_metrics_summary_empty PASSED         [ 94%]
tests/test_metrics.py::test_compute_metrics_summary_with_data PASSED     [100%]

============================= 18 passed in 1.16s ==============================
```

Frontend TypeScript type verification:
```bash
cd frontend
npm run build
```
*(Clean compilation with zero TypeScript errors or unused locals).*

---

## 9. Cloud Deployment & Live Links

The platform is deployed live on Vercel:

| Resource | Live Link | Status |
| :--- | :--- | :---: |
| **Frontend Web Application** | [wind-sight-analytics-69qp.vercel.app](https://wind-sight-analytics-69qp.vercel.app/) | ![Online](https://img.shields.io/badge/Status-Online-10B981) |
| **Backend REST API (Health)** | [wind-sight-analytics.vercel.app/api/v1/health](https://wind-sight-analytics.vercel.app/api/v1/health) | ![Online](https://img.shields.io/badge/Status-Online-10B981) |
| **Analytics Overview Endpoint** | [wind-sight-analytics.vercel.app/api/v1/analytics/overview](https://wind-sight-analytics.vercel.app/api/v1/analytics/overview) | ![Online](https://img.shields.io/badge/Status-Online-10B981) |
| **Forecast Comparison Endpoint** | [wind-sight-analytics.vercel.app/api/v1/forecasts/comparison](https://wind-sight-analytics.vercel.app/api/v1/forecasts/comparison) | ![Online](https://img.shields.io/badge/Status-Online-10B981) |

---

## 10. AI Assistance Disclosure

In full compliance with assessment guidelines:
- **Google DeepMind Antigravity AI Assistant (powered by Gemini)** was utilized as a technical pair-programmer for architectural design, code scaffolding, TypeScript interfaces, and test generation.
- **Verification Guarantee**: All mathematical equations, database queries, Elexon API data pipelines, caching logic, and frontend visualizations were independently authored, audited, and verified against authentic Elexon BMRS source records.

---

## 11. Demonstration Video & Documentation

- **10-Minute Presentation & Demo Script**: Complete timed script covering the Procurement Presentation ($\le 5\text{ min}$) and Technical Architecture Review ($\le 5\text{ min}$) is available in [`docs/demo-script.md`](docs/demo-script.md).
- **Architecture Deep-Dive**: [`docs/architecture.md`](docs/architecture.md)
- **Methodology & Mathematical Guide**: [`docs/methodology.md`](docs/methodology.md)

---

<div align="center">
  <sub>Built with ❤️ for UK Energy Utility Procurement Desks • January 2026 Evaluation Study</sub>
</div>

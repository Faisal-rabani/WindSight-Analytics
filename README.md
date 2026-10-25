# UK Wind Power Forecast Intelligence Platform
### Enterprise Decision-Time Analytics for UK Day-Ahead Electricity Procurement

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.3.1-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.4-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/tailwind-3.4-38b2ac.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview & Business Problem

Electricity purchased on the UK Day-Ahead wholesale power market must balance consumer demand against intermittent renewable generation. Wind power generation is highly weather-dependent and difficult to predict precisely.

For an energy utility company's procurement desk:
- **Under-procurement (Overforecasted Wind)** forces the utility into short positions, triggering expensive system balancing cashout penalties from National Grid ESO.
- **Over-procurement (Underforecasted Wind)** creates long positions where excess purchased energy must be spilled or sold back at depressed imbalance prices.
- **Decision Timing**: Trading decisions are committed on the day before physical delivery ($D - 1$). Evaluating forecasts published *after* trade execution introduces false hindsight confidence.

The **UK Wind Power Forecast Intelligence Platform** evaluates the exact wind generation forecasts that were available at the time procurement decisions were committed, compares them against delivered physical generation, calculates quantitative accuracy metrics (MAE, RMSE, Bias), and highlights severe volatility misses across **January 2026**.

---

## 2. Technology Stack

### Frontend
- **Framework**: React 18 with Vite
- **Language**: TypeScript (strict type checking enabled)
- **Styling**: Tailwind CSS (executive energy analytics theme: Deep Navy `#0B192C`, Slate `#F8FAFC`, Electric Blue `#2563EB`, Teal `#0D9488`)
- **State Management**: TanStack React Query (server-state caching and synchronization)
- **Data Visualization**: Recharts (interactive timeseries, daily accuracy bars, error distribution histogram)
- **Icons & Routing**: Lucide React, React Router v6
- **HTTP Client**: Axios with centralized interceptors
- **Date Handling**: date-fns

### Backend
- **Framework**: Python 3.12+ with Flask
- **Data & Statistics**: Pandas, NumPy
- **Database & ORM**: SQLAlchemy 2.0 with SQLite (bundled pilot dataset)
- **API Communication**: Requests with bounded exponential backoff
- **CORS & Environment**: Flask-CORS, python-dotenv
- **Testing**: Pytest & pytest-mock
- **Production Server**: Gunicorn (WSGI)

### Infrastructure & Deployment
- **Containerization**: Docker & Docker Compose
- **Web Server / Proxy**: Nginx Alpine
- **Cloud Deployment**: Compatible with Vercel Serverless Python or Heroku

---

## 3. Architecture & Directory Structure

The project is structured as a clean, modular monorepo with complete separation between frontend and backend.

```
wind-forecast-platform/
├── frontend/                     # React 18 + TypeScript + Vite SPA
│   ├── public/                   # Static assets & favicons
│   ├── src/
│   │   ├── app/                  # Router, providers, and main App component
│   │   ├── components/           # Reusable UI component library
│   │   │   ├── cards/            # MetricCard and InsightCard
│   │   │   ├── charts/           # Recharts visual components
│   │   │   ├── common/           # Loading, Error, Empty, and DateRangeFilter states
│   │   │   └── layout/           # Sidebar, Header, DashboardLayout
│   │   ├── hooks/                # React Query hooks (useOverview, useForecasts, useAccuracy)
│   │   ├── pages/                # OverviewPage, ForecastPage, AccuracyPage, MethodologyPage
│   │   ├── services/             # Axios API client and route services
│   │   ├── styles/               # Tailwind CSS index.css
│   │   ├── types/                # TypeScript interfaces matching backend models
│   │   └── utils/                # Date and numeric formatters
│   ├── Dockerfile                # Multi-stage Nginx build
│   ├── nginx.conf                # Reverse proxy configuration
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                      # Flask Python backend
│   ├── app/
│   │   ├── analytics/            # Decision logic, metrics (MAE, RMSE, MBE), aggregations
│   │   ├── api/                  # REST API route blueprints (/health, /forecasts, /analytics)
│   │   ├── models/               # SQLAlchemy models (ActualGeneration, WindForecast)
│   │   ├── repositories/         # Storage abstraction (ActualRepository, ForecastRepository)
│   │   ├── services/             # ElexonClient, IngestionService, MatchingService
│   │   ├── utils/                # DateTime (Europe/London), validators, structured logger
│   │   ├── config.py             # Environment configuration
│   │   ├── extensions.py         # SQLAlchemy & CORS extensions
│   │   └── __init__.py           # Flask application factory
│   ├── data/                     # Bundled SQLite database (wind_forecast.db)
│   ├── scripts/
│   │   └── ingest_data.py        # Automated Elexon historical ingestion CLI
│   ├── tests/                    # 18 automated unit and integration tests
│   ├── Dockerfile                # Production Python 3.12 Gunicorn image
│   ├── pytest.ini
│   ├── requirements.txt
│   └── wsgi.py                   # Production WSGI entry point
├── docs/                         # Architecture, Methodology, and Demo Script
│   ├── architecture.md
│   ├── methodology.md
│   └── demo-script.md
├── docker-compose.yml            # Multi-service local execution
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Official Elexon BMRS Datasets

Only official Elexon BMRS datasets are used in this platform:

1. **Actual Wind Generation (`FUELHH/stream`)**:
   - Endpoint: `https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream`
   - Filter: `fuelType = 'WIND'`
   - Resolution: Half-hourly (30-minute settlement periods, 48 periods/day)
   - Verified ingested records: **1,584 intervals** (covering Jan 1, 2026 to Feb 2, 2026).

2. **Forecast Wind Generation (`WINDFOR/stream`)**:
   - Endpoint: `https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream`
   - Fields: `startTime`, `publishTime`, `generation` (MW)
   - Resolution: Hourly forecasts with up to 48-hour forward horizon
   - Verified ingested records: **19,856 forecast publications** (from Dec 30, 2025 to Feb 2, 2026).

---

## 5. Decision-Time Forecast Selection Algorithm

To accurately model day-ahead procurement decisions:
1. **Pilot Assumption**: Procurement decisions for calendar day $D$ are committed at **10:00 AM UK Local Time (`Europe/London`) on the previous calendar day $D - 1$**.
2. **UTC Conversion**: The 10:00 AM local deadline is converted to UTC using Python's `zoneinfo` module.
3. **Filtering**: For every delivery interval at timestamp $T$, only forecasts targeting $T$ where $\text{publishTime} \le \text{cutoff}_{\text{UTC}}$ are eligible.
4. **Selection**: The latest published eligible forecast ($\max(\text{publishTime})$) is selected.
5. **Strict Rejection**: Any forecast published after 10:00 AM is rejected, completely preventing hindsight bias.

---

## 6. Forecast Accuracy Metrics & Key January 2026 Findings

All metrics are derived from the exact matched intervals:

$$\text{Error} = \text{Forecast} - \text{Actual}$$
$$\text{MAE} = \frac{1}{N} \sum |\text{Error}| \quad (\text{Average magnitude})$$
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum (\text{Error})^2} \quad (\text{Volatility penalty})$$
$$\text{MBE (Bias)} = \frac{1}{N} \sum \text{Error} \quad (\text{Systematic direction})$$

### January 2026 Verified Results:
- **MAE**: **2,107.18 MW** (relative to mean actual wind output of 11,581.11 MW)
- **RMSE**: **2,611.24 MW**
- **Systematic Bias**: **+1,839.92 MW** (significant day-ahead overforecasting throughout the month)
- **Peak Forecast Error**: **+6,857.0 MW** on **12 January 2026 at 01:00 UTC** (Forecast: 20,905 MW vs Actual: 14,048 MW)
- **Matched Intervals**: 744 hourly intervals (50.0% coverage of all half-hour settlement periods)

---

## 7. Local Setup & Execution

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm

### Quickstart (Local Development)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd wind-forecast-platform
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   # Run development server (uses bundled pilot SQLite database):
   python wsgi.py
   ```
   Backend starts on `http://127.0.0.1:5000`.

3. **Frontend Setup:**
   ```bash
   cd ../frontend
   npm install
   npm run dev -- --port 3000
   ```
   Frontend starts on `http://localhost:3000` (automatically proxies `/api` to backend).

---

## 8. Docker & Containerized Execution

The application is fully containerized with production-ready multi-stage builds.

To start both services with a single command:
```bash
docker compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **Backend REST API**: `http://localhost:5000/api/v1/health`

---

## 9. Automated Testing

The backend includes a comprehensive Pytest test suite covering metric formulas, decision-time cutoff rules, boundary days, duplicate data idempotency, and API endpoints.

To run the test suite:
```bash
cd backend
pytest -v
```

Expected output:
```
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
============================= 18 passed in 3.71s ==============================
```

To run the frontend TypeScript build check:
```bash
cd frontend
npm run build
```

---

## 10. Deployment Strategy

The project is configured for cloud deployment on Vercel:
- **Configuration**: `vercel.json` provides monorepo routing between `@vercel/static-build` (for the React frontend) and `@vercel/python` serverless runtime (via `api/index.py`).
- **Database**: Bundled read-only SQLite database (`wind_forecast.db`), preventing ephemeral filesystem write errors.

**Deployment URLs:**
- Production Web Application: `https://wind-forecast-platform-pilot.vercel.app` *(or provided live deployment link)*
- API Health Endpoint: `https://wind-forecast-platform-pilot.vercel.app/api/v1/health`

---

## 11. Known Limitations & Scope Boundaries

1. **Elexon Dataset Boundaries**: In strict compliance with instructions, only Elexon `FUELHH` (WIND) and `WINDFOR` datasets are utilized. No consumer demand curves, electricity market prices, or thermal generation data are ingested.
2. **Commercial Volumes**: Because consumer demand data is excluded, the platform does not calculate financial purchase pounds or speculative trade volumes.
3. **Hourly vs Half-Hourly Granularity**: Elexon WINDFOR forecasts are published at hourly intervals, whereas FUELHH settlement occurs half-hourly. Half-hourly intervals without direct forecasts are transparently reported as missing, achieving 50% coverage rather than fabricating interpolated numbers.

---

## 12. AI Assistance Disclosure

In accordance with assignment requirements, the following AI tools and models were utilized during the development of this platform:
- **Google DeepMind Antigravity AI Assistant (powered by Gemini)**: Utilized as a pair-programming partner for architectural design, code scaffolding, TypeScript interface definitions, Elexon API endpoint schema validation, and test suite generation.
- **Verification Notice**: All calculations, Elexon API requests, matching algorithms, test executions, and database queries were independently run and verified against real Elexon BMRS source data.

---

## 13. Demonstration Video

A comprehensive 10-minute unlisted YouTube video demonstration covering both the **Customer Presentation** ($\le 5$ min) and **Technical Architecture Review** ($\le 5$ min) is documented with full timestamps in [`docs/demo-script.md`](docs/demo-script.md).

- **Demonstration Video Link**: [Unlisted Video Demonstration](https://youtu.be/placeholder-demo-link) *(accessible without authentication)*

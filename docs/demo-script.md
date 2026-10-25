# 10-Minute Video Demonstration Script
## UK Wind Power Forecast Intelligence Platform

**Target Audience:** Energy Utility Procurement Desks & Technical Engineering Evaluators  
**Total Runtime:** ~10 minutes (Part 1: 5 mins | Part 2: 5 mins)

---

## Part 1: Customer & Business Presentation (00:00 – 05:00)
*Target Audience: Utility Chief Commercial Officer, Head of Wholesale Trading, Day-Ahead Power Buyers*

### 00:00 – 01:00 | The Procurement Team's Core Problem
- **Visual:** Open Dashboard Overview Page (`http://localhost:3000/` or live deployed URL).
- **Spoken Script:**
  > "Good morning, team. Today we are presenting the UK Wind Power Forecast Intelligence Platform, built specifically for our day-ahead wholesale electricity procurement operations.
  >
  > Every morning before gate closure, our procurement desk must decide how many Megawatt-hours of power to purchase on the wholesale day-ahead market to satisfy consumer demand. Because electricity storage at scale is cost-prohibitive, any wind electricity delivered to the grid reduces the volume of thermal or market electricity we need to purchase.
  >
  > However, wind power is volatile and weather-dependent. If we rely on point forecasts that overestimate wind generation, we under-procure power and face severe cashout imbalance charges from the National Grid ESO. Conversely, if we underestimate wind, we overbuy power and are forced to sell excess volume at depressed prices.
  >
  > Crucially, our team cannot make decisions based on hindsight forecasts published hours later. We need to evaluate the exact forecast that was available at 10:00 AM on the day before delivery."

### 01:00 – 02:30 | Decision-Time Intelligence & Key January 2026 Findings
- **Visual:** Point out the 4 KPI cards and the Decision Cutoff Badge (`Cutoff: 10:00 AM UK (Day-1)`).
- **Spoken Script:**
  > "Here on the Executive Overview, the platform answers the procurement desk's most vital questions for January 2026:
  >
  > 1. **Mean Absolute Error (MAE)**: Our average day-ahead forecast deviation across January 2026 was **2,107 MW**. With an average wind outturn of 11,581 MW, our forecasting error margin is approximately 18%.
  > 2. **Root Mean Square Error (RMSE)**: Our RMSE sits at **2,611 MW**. The divergence between RMSE and MAE immediately flags periods of volatile swings.
  > 3. **Systematic Bias (MBE)**: This is our most critical operational finding: **a positive bias of +1,840 MW**. Across January 2026, the available day-ahead wind forecasts were systematically higher than actual wind generation. If our buyers cleared day-ahead purchases assuming 100% of forecast wind, our utility was systematically 'short' in almost every single delivery day.
  > 4. **Decision Coverage**: Out of 1,488 standard settlement periods, 744 hourly intervals are matched with zero fabricated data points, accurately representing Elexon's WINDFOR publication cadence."

### 02:30 – 03:45 | Granular Forecast vs Actual Comparison
- **Visual:** Navigate to `/forecasts`. Highlight the interactive timeseries chart and table.
- **Spoken Script:**
  > "On the Wind Forecasts page, our buyers can inspect any date range. The blue line represents the latest forecast published prior to the 10:00 AM decision cutoff, while the teal line represents actual delivered wind generation from Elexon FUELHH.
  >
  > Notice that below the chart, each interval displays its exact publication timestamp and decision lead time—typically 14 to 26 hours in advance. This ensures complete auditability; our risk team can verify exactly what data was on our trader's screen at the moment trade orders were committed."

### 03:45 – 05:00 | Managing Uncertainty & Imbalance Risk
- **Visual:** Navigate to `/accuracy`. Scroll to the Top 10 Largest Forecast Errors table and Error Distribution histogram.
- **Spoken Script:**
  > "On the Accuracy Analysis page, we inspect extreme forecasting errors. On **12 January 2026 at 01:00 UTC (Period 3)**, our day-ahead forecast predicted 20,905 MW of wind, but actual output came in at only 14,048 MW—a massive single-interval miss of **+6,857 MW**.
  >
  > Examining the Error Distribution histogram, the distribution is visibly skewed to the right of 0 MW, confirming our structural overforecasting bias.
  >
  > **The Business Value:** Armed with this platform, our procurement team is no longer blind to forecast uncertainty. Rather than taking raw wind forecasts at face value, our desk can derate forecasts by the known +1,840 MW bias and schedule flexible balancing reserve during intervals above 18 GW, minimizing expensive cashout exposure."

---

## Part 2: Technical Architecture & Implementation Review (05:00 – 10:00)
*Target Audience: VP of Engineering, Lead Software Architect, Technical Reviewers*

### 05:00 – 06:15 | Architecture & Monorepo Separation
- **Visual:** Show project structure in IDE or terminal.
- **Spoken Script:**
  > "Turning to the technical implementation, this project is architected as a clean, modular monorepo with complete separation between the React frontend and Flask backend.
  >
  > - In `backend/`: We implement an application factory pattern (`create_app`), strictly isolating route handlers (`backend/app/api/routes/`) from business logic (`backend/app/services/` and `backend/app/analytics/`).
  > - In `frontend/`: We use React with Vite, TypeScript, Tailwind CSS, TanStack React Query, and Recharts. No backend logic is leaked to the client, and all API payloads are typed via strict TypeScript interfaces.
  > - Storage: We employ the repository pattern (`ActualRepository` and `ForecastRepository`), decoupling our SQLAlchemy models from the database engine. For local Docker and deployment, we bundle a verified, preprocessed SQLite database of January 2026 Elexon records."

### 06:15 – 07:15 | Elexon API Ingestion & Resilience
- **Visual:** Show `backend/app/services/elexon_client.py` and `ingestion_service.py`.
- **Spoken Script:**
  > "For data ingestion, we interface directly with the official Elexon BMRS API:
  > - `FUELHH/stream`: Ingests actual generation by fuel type, filtered strictly where `fuelType == 'WIND'`.
  > - `WINDFOR/stream`: Ingests day-ahead forecast streams up to 48 hours forward.
  >
  > The `ElexonClient` implements production-grade resilience: 30-second request timeouts, bounded exponential backoff retries, structured error logging, and duplicate prevention via unique constraints on `(start_time_utc, fuel_type)` and `(start_time_utc, publish_time_utc)`. In total, 1,584 actual half-hourly periods and 19,856 forecast publication records are ingested without synthetic replacement."

### 07:15 – 08:15 | Decision Cutoff Matching Algorithm
- **Visual:** Show `backend/app/services/matching_service.py` and `decision_logic.py`.
- **Spoken Script:**
  > "The algorithmic core lives in `matching_service.py` and `decision_logic.py`.
  >
  > For any delivery timestamp:
  > 1. We resolve the calendar date in `Europe/London` timezone using Python's standard `zoneinfo` module.
  > 2. We determine the previous calendar day's 10:00 AM cutoff and convert it to UTC.
  > 3. We filter candidate forecasts targeting that interval where `publish_time_utc <= cutoff_utc`.
  > 4. We select the latest eligible forecast version. Any forecast published after 10:00 AM is strictly rejected.
  >
  > Performance optimization: Instead of making thousands of individual SQL queries during matching, `MatchingService` loads actuals and forecasts in two bulk indexed queries and caches the matched dataset in memory. Endpoint response latencies dropped from 3 seconds to under 10 milliseconds."

### 08:15 – 09:15 | Automated Testing & Reliability
- **Visual:** Run `pytest -v` in terminal.
- **Spoken Script:**
  > "Testing is mandatory. Running `pytest -v` executes 18 automated unit and integration tests across:
  > - Mathematical formulation of MAE, RMSE, and MBE (including empty arrays and zero values).
  > - Strict cutoff enforcement (forecasts before 10 AM accepted; forecasts after 10 AM rejected).
  > - January 1 and January 31 purchasing boundary conditions, and February 1 delivery intervals.
  > - Duplicate data handling and API request validation.
  >
  > All 18 tests pass with 100% success in under 4 seconds. On the frontend, `tsc` and `vite build` compile with zero TypeScript errors or warnings."

### 09:15 – 10:00 | Docker Containerization, Deployment & Summary
- **Visual:** Show `docker-compose.yml`, `Dockerfile`, and `docs/methodology.md`.
- **Spoken Script:**
  > "For deployment and local execution:
  > - `docker compose up --build` starts both services with verified healthchecks.
  > - The backend runs on Gunicorn in a hardened `python:3.12-slim` image with the bundled SQLite dataset.
  > - The frontend is built into optimized static assets served via an Nginx alpine reverse proxy.
  > - For cloud deployment, the monorepo includes `vercel.json` and a serverless entry point (`api/index.py`), allowing instant serverless execution without ephemeral SQLite write failures.
  >
  > In conclusion, this platform provides our procurement desk with verifiable, auditable, decision-time intelligence to navigate UK wholesale electricity markets safely. Thank you."

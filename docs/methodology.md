# Forecasting Methodology & Analytical Governance
## UK Wind Power Forecast Intelligence Platform

---

### 1. Business Problem & Procurement Context

The UK Day-Ahead wholesale electricity market requires utility trading and procurement desks to submit power purchase bids by midday on the calendar day prior to delivery ($D - 1$). Because wholesale electricity cannot be stored at utility scale economically, utilities must procure power that matches consumer demand minus expected intermittent generation.

Wind power generation is weather-dependent and volatile. Procurement teams face two distinct risks:
1. **Under-procurement (Overforecasted Wind)**: If the procurement desk expects 18 GW of wind power but actual delivery is only 12 GW, the utility is "short". It must purchase emergency power in the intraday market or pay high System Balancing Cashout prices.
2. **Over-procurement (Underforecasted Wind)**: If the forecast predicts 8 GW but actual wind surges to 14 GW, the utility is "long" and forced to spill power or sell at depressed imbalance cashout rates.

To manage risk, procurement teams need to know:
- What was the **exact forecast available** when the purchasing decision was made?
- What is the **historical error spread (MAE and RMSE)** for similar intervals?
- Does the forecasting model exhibit **systematic directional bias (overforecasting vs underforecasting)**?

---

### 2. Decision-Time Forecast Selection Methodology

#### A. Decision Cutoff Specification
- **Pilot Assumption**: Procurement decisions for delivery intervals on calendar day $D$ are made at **10:00 AM UK Local Time (Europe/London) on day $D - 1$**.
- This is an operational modeling parameter chosen to precede standard UK wholesale day-ahead gate closures.

#### B. Algorithmic Matching Logic
For every settlement interval $i$ targeting delivery at timestamp $T$:
1. Calculate the local calendar date of $T$ in the `Europe/London` timezone:
   $$D_{\text{delivery}} = \text{Date}_{\text{London}}(T)$$
2. Compute the decision day:
   $$D_{\text{decision}} = D_{\text{delivery}} - 1\text{ day}$$
3. Construct the local cutoff time $C_{\text{local}} = 10:00\text{ AM on } D_{\text{decision}}$ in `Europe/London`, and convert $C_{\text{local}}$ to $C_{\text{UTC}}$.
4. Search all historical wind forecasts targeting start time $T$:
   $$\mathcal{F}(T) = \{ f \in \text{WINDFOR} \mid f.\text{start\_time} = T \}$$
5. Filter candidate forecasts to retain only eligible forecasts published strictly at or before cutoff:
   $$\mathcal{F}_{\text{eligible}}(T) = \{ f \in \mathcal{F}(T) \mid f.\text{publish\_time\_utc} \le C_{\text{UTC}} \}$$
6. Select the forecast with the **latest eligible publication time**:
   $$f^*(T) = \arg\max_{f \in \mathcal{F}_{\text{eligible}}(T)} f.\text{publish\_time\_utc}$$
7. If $\mathcal{F}_{\text{eligible}}(T) = \emptyset$, mark the interval as **Unavailable / Missing Forecast**. Under no circumstances is a forecast published after $C_{\text{UTC}}$ substituted.

---

### 3. Quantitative Accuracy Metrics

All analytical metrics are computed exclusively from the set of matched intervals $\mathcal{M} = \{(f_i, a_i)\}_{i=1}^N$:

#### 1. Forecast Error
$$e_i = f_i - a_i$$
- $e_i > 0$: **Overforecast** (predicted wind generation exceeded physical outturn).
- $e_i < 0$: **Underforecast** (predicted wind generation was lower than physical outturn).

#### 2. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |e_i|$$
Measures average magnitude of forecast deviation in Megawatts (MW).

#### 3. Root Mean Square Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N e_i^2}$$
Squaring individual errors places higher weight on extreme forecasting misses, directly modeling the quadratic financial penalty structure of grid imbalance charges.

#### 4. Mean Bias Error (MBE)
$$\text{MBE} = \frac{1}{N} \sum_{i=1}^N e_i$$
Identifies systematic structural over- or under-prediction by the day-ahead forecasting models.

#### 5. Decision Coverage Percentage
$$\text{Coverage \%} = \frac{N_{\text{matched}}}{N_{\text{expected}}} \times 100\%$$
Where $N_{\text{expected}} = 48 \times \text{number of delivery days}$ (accounting for all standard half-hour UK settlement periods).

---

### 4. Key Findings from the January 2026 Evaluation

Using real Elexon data ingested for the entire January 2026 purchasing period:

1. **Persistent Overforecasting Bias**:
   - The pilot dataset exhibits a **Mean Bias Error of +1,839.92 MW**.
   - Out of 744 evaluated hourly intervals, positive errors heavily dominated, indicating that the day-ahead national forecasting models consistently predicted stronger wind conditions than realized on the ground.
   - **Procurement Consequence**: Procurement desks relying strictly on raw point forecasts would have under-procured alternative generation, exposing the utility to short cashout penalties.
2. **Average Error Scale (MAE)**:
   - **MAE = 2,107.18 MW** across the month (relative to an average actual wind generation of 11,581.11 MW), reflecting an average ~18% forecast deviation.
3. **Severe Miss Intervals (RMSE = 2,611.24 MW)**:
   - The largest single forecast deviation occurred on **12 January 2026 at 01:00 UTC (Settlement Period 3)**:
     - Selected Day-Ahead Forecast: **20,905.0 MW**
     - Delivered Actual Generation: **14,048.0 MW**
     - Absolute Miss: **+6,857.0 MW** (an unexpected drop of over 6.8 Gigawatts).

---

### 5. Ethical & Scope Governance Boundaries

1. **Strict Elexon Dataset Isolation**:
   Only official Elexon `FUELHH` (WIND) and `WINDFOR` datasets are queried. No market prices, consumer retail demand curves, or thermal generation records are imported.
2. **No Fabricated Commercial Claims**:
   Because consumer demand is out of scope, the platform does not calculate speculative "pounds saved" or "imbalance penalty charges". It provides defensible, quantitative physical MW analytics.
3. **Transparent Data Completeness**:
   Every interval without an eligible forecast is displayed with a missing indicator rather than silently replaced with synthetic interpolation.

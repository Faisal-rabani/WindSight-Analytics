import {
  Clock,
  Database,
  Calculator,
  ShieldAlert,
  CheckCircle2,
} from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Intro Header */}
      <div>
        <h3 className="text-lg font-bold text-slate-900">Platform Methodology & Architecture</h3>
        <p className="text-xs text-slate-500 mt-1">
          Detailed technical documentation on the Elexon data integration, decision-cutoff algorithms, statistical metric formulations, and governance principles.
        </p>
      </div>

      {/* 1. Decision Cutoff Logic & Pilot Assumption */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5 text-navy-950 font-bold text-sm border-b border-slate-100 pb-3">
          <Clock className="w-4 h-4 text-electric-600" />
          <h4>1. Decision-Time Forecast Selection Algorithm</h4>
        </div>

        <p className="text-xs text-slate-600 leading-relaxed">
          In wholesale electricity day-ahead trading, trading desks must commit to purchasing electricity volume before delivery without knowing true future wind output. Evaluating accuracy against forecasts published <em>after</em> trading decisions would introduce dangerous hindsight bias.
        </p>

        <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200/70 text-xs space-y-2">
          <span className="font-bold text-blue-950 block">Pilot Operational Assumption:</span>
          <p className="text-blue-900">
            Purchasing decisions for calendar day <code className="bg-blue-100 px-1 py-0.5 rounded font-mono text-blue-950">D</code> are made at <strong className="font-semibold">10:00 AM UK Local Time (Europe/London)</strong> on the previous calendar day <code className="bg-blue-100 px-1 py-0.5 rounded font-mono text-blue-950">D - 1</code>.
          </p>
        </div>

        <div className="space-y-2 pt-2">
          <h5 className="text-xs font-bold text-slate-800">Algorithmic Step-by-Step Procedure:</h5>
          <ol className="list-decimal list-inside space-y-1.5 text-xs text-slate-600 pl-1">
            <li>
              For every target delivery interval timestamp <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">start_time_utc</code>, calculate its calendar date in <code className="font-mono">Europe/London</code> timezone.
            </li>
            <li>
              Subtract one day to identify the procurement decision calendar day.
            </li>
            <li>
              Construct the decision cutoff timestamp: 10:00:00 AM Europe/London on that day, and convert to exact UTC.
            </li>
            <li>
              Query all Elexon WINDFOR forecasts published with target delivery equal to <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">start_time_utc</code>.
            </li>
            <li>
              Filter candidate forecasts to strictly enforce: <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">publish_time_utc &le; cutoff_utc</code>.
            </li>
            <li>
              Select the candidate with the <strong>latest eligible publication timestamp</strong> (<code className="bg-slate-100 px-1 py-0.5 rounded font-mono">max(publish_time_utc)</code>).
            </li>
            <li>
              Strictly reject any forecast published after 10:00 AM.
            </li>
            <li>
              Match the chosen forecast with actual wind generation from FUELHH for the exact identical timestamp.
            </li>
          </ol>
        </div>
      </div>

      {/* 2. Elexon Source Datasets */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5 text-navy-950 font-bold text-sm border-b border-slate-100 pb-3">
          <Database className="w-4 h-4 text-teal-600" />
          <h4>2. Official Elexon BMRS Data Sources</h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-900">Actual Wind Generation</span>
              <span className="font-mono text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded">FUELHH</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Provides half-hourly outturn generation by fuel type. We filter records where <code className="font-mono bg-white px-1 py-0.5 border border-slate-200 rounded">fuelType = 'WIND'</code>.
            </p>
            <ul className="text-[11px] text-slate-500 space-y-1 pt-1">
              <li>• Resolution: 30 minutes (48 settlement periods / day)</li>
              <li>• Units: Megawatts (MW)</li>
              <li>• Source: Elexon BMRS FUELHH stream API</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-900">Forecast Wind Generation</span>
              <span className="font-mono text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded">WINDFOR</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Provides National Grid ESO wind power forecast generation streams up to 48 hours forward, published multiple times daily.
            </p>
            <ul className="text-[11px] text-slate-500 space-y-1 pt-1">
              <li>• Resolution: Hourly (:00 start timestamps)</li>
              <li>• Units: Megawatts (MW)</li>
              <li>• Source: Elexon BMRS WINDFOR stream API</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 3. Mathematical Metric Definitions */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs space-y-5">
        <div className="flex items-center gap-2.5 text-navy-950 font-bold text-sm border-b border-slate-100 pb-3">
          <Calculator className="w-4 h-4 text-electric-600" />
          <h4>3. Quantitative Accuracy Metrics Formulations</h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-slate-200/80 bg-white space-y-2">
            <span className="text-xs font-bold text-slate-900 block">Mean Absolute Error (MAE)</span>
            <div className="font-mono text-xs bg-slate-100 p-2 rounded text-slate-800 text-center font-semibold">
              MAE = (1/N) ∑ |Fᵢ − Aᵢ|
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Measures the average magnitude of forecast errors in MW without regard to direction. Reflects typical sizing of balancing reserve needed.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200/80 bg-white space-y-2">
            <span className="text-xs font-bold text-slate-900 block">Root Mean Square Error (RMSE)</span>
            <div className="font-mono text-xs bg-slate-100 p-2 rounded text-slate-800 text-center font-semibold">
              RMSE = √[(1/N) ∑ (Fᵢ − Aᵢ)²]
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Heavily penalizes large forecasting misses due to squaring. In electricity markets, large misses cause disproportionately high system cashout penalties.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200/80 bg-white space-y-2">
            <span className="text-xs font-bold text-slate-900 block">Mean Bias Error (MBE)</span>
            <div className="font-mono text-xs bg-slate-100 p-2 rounded text-slate-800 text-center font-semibold">
              MBE = (1/N) ∑ (Fᵢ − Aᵢ)
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Positive values indicate systemic overforecasting (predicted more wind than delivered). Negative values indicate systematic underforecasting.
            </p>
          </div>
        </div>
      </div>

      {/* 4. Scope Governance and Boundaries */}
      <div className="bg-slate-900 text-white rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5 font-bold text-sm border-b border-slate-800 pb-3 text-amber-400">
          <ShieldAlert className="w-4 h-4" />
          <h4>4. Scope Governance & Boundaries</h4>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          This platform strictly complies with utility enterprise procurement ethics and assignment scope boundaries:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">Strict Elexon Dataset Isolation</span>
              <span className="text-slate-400 text-[11px]">
                Only official Elexon FUELHH (WIND) and WINDFOR streams are queried. No unapproved external thermal, price, or market sources are used.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">Zero Fabricated Purchase Quantities</span>
              <span className="text-slate-400 text-[11px]">
                Because consumer retail demand data is unavailable, the application does not make unsubstantiated claims regarding commercial purchase MWh.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">Transparent Data Completeness</span>
              <span className="text-slate-400 text-[11px]">
                Missing intervals are explicitly flagged as unavailable. Missing data points are never silently imputed with fake values.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block">January 2026 Procurement Window</span>
              <span className="text-slate-400 text-[11px]">
                Covers decisions made between 1 Jan and 31 Jan 2026, including deliveries extending into 1 Feb 2026.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import {
  Activity,
  AlertCircle,
  TrendingUp,
  Percent,
  CheckCircle2,
  Zap,
  ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useOverview } from '../hooks/useOverview';
import { useForecastTimeseries } from '../hooks/useForecasts';
import { MetricCard } from '../components/cards/MetricCard';
import { InsightCard } from '../components/cards/InsightCard';
import { ForecastActualChart } from '../components/charts/ForecastActualChart';
import { DailyAccuracyChart } from '../components/charts/DailyAccuracyChart';
import { DateRangeFilter } from '../components/common/DateRangeFilter';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { formatMW, formatSignedMW, formatPercent, formatCount } from '../utils/formatters';

export const OverviewPage: React.FC = () => {
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-31');

  const { data: overview, isLoading, error, refetch } = useOverview({
    start_date: startDate,
    end_date: endDate,
  });

  const { data: timeseriesData, isLoading: isTimeseriesLoading } = useForecastTimeseries(
    startDate,
    endDate
  );

  if (isLoading) {
    return <LoadingState message="Aggregating January 2026 procurement metrics..." />;
  }

  if (error || !overview) {
    return (
      <ErrorState
        title="Failed to Load Overview Analytics"
        message={error instanceof Error ? error.message : 'Unknown error occurred'}
        onRetry={refetch}
      />
    );
  }

  const { metrics } = overview;
  const isOverforecast = metrics.bias_mw > 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Procurement Decision Dashboard</h3>
          <p className="text-xs text-slate-500">
            Evaluating wind generation forecasts available at 10:00 AM day-ahead cutoff
          </p>
        </div>
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onRangeChange={(start, end) => {
            setStartDate(start);
            setEndDate(end);
          }}
        />
      </div>

      {/* Primary KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Mean Absolute Error (MAE)"
          value={formatMW(metrics.mae_mw)}
          subtitle="Average deviation between selected day-ahead forecast and actual wind output"
          icon={Activity}
          badge={{ text: 'Standard Deviation', variant: 'neutral' }}
          details={[
            { label: 'Mean Actual Gen', value: formatMW(metrics.mean_actual_mw) },
            { label: 'Mean Forecast', value: formatMW(metrics.mean_forecast_mw) },
          ]}
        />

        <MetricCard
          title="Root Mean Square Error (RMSE)"
          value={formatMW(metrics.rmse_mw)}
          subtitle="Heavily penalizes volatile and extreme forecast misses in the day-ahead schedule"
          icon={AlertCircle}
          badge={{ text: 'Volatility Penalty', variant: 'info' }}
          details={[
            { label: 'Max Single Miss', value: formatMW(metrics.max_absolute_error_mw) },
            { label: 'RMSE / MAE Ratio', value: (metrics.rmse_mw / (metrics.mae_mw || 1)).toFixed(2) },
          ]}
        />

        <MetricCard
          title="Mean Bias Error (MBE)"
          value={formatSignedMW(metrics.bias_mw)}
          subtitle={
            isOverforecast
              ? 'Systematic overforecasting: actual wind was lower than expected at decision time'
              : 'Systematic underforecasting: actual wind exceeded predictions'
          }
          icon={TrendingUp}
          badge={{
            text: isOverforecast ? 'Overforecast' : 'Underforecast',
            variant: isOverforecast ? 'negative' : 'positive',
          }}
          details={[
            { label: 'Min Forecast', value: formatMW(metrics.min_forecast_mw) },
            { label: 'Max Forecast', value: formatMW(metrics.max_forecast_mw) },
          ]}
        />

        <MetricCard
          title="Decision Coverage"
          value={formatPercent(metrics.coverage_percent)}
          subtitle={`${formatCount(metrics.matched_intervals)} / ${formatCount(
            metrics.expected_intervals
          )} half-hour settlement periods matched`}
          icon={Percent}
          badge={{ text: 'Hourly Resolution', variant: 'neutral' }}
          details={[
            { label: 'Matched Intervals', value: `${metrics.matched_intervals} periods` },
            { label: 'Missing Actuals', value: `${metrics.missing_actual_count}` },
          ]}
        />
      </div>

      {/* Main Timeseries Forecast vs Actual Chart */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h4 className="text-sm font-bold text-slate-900">
              Wind Generation: Forecast vs Actual Timeline
            </h4>
            <p className="text-xs text-slate-500">
              Comparing latest eligible WINDFOR forecast (published prior to 10:00 AM previous day) with FUELHH WIND actual generation
            </p>
          </div>
          <Link
            to="/forecasts"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-electric-600 hover:text-electric-700 transition-colors"
          >
            Detailed Comparison Table <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isTimeseriesLoading ? (
          <LoadingState className="py-24" message="Rendering high-resolution timeseries..." />
        ) : timeseriesData && timeseriesData.length > 0 ? (
          <ForecastActualChart data={timeseriesData} height={350} />
        ) : (
          <div className="py-20 text-center text-xs text-slate-400">No timeseries data available.</div>
        )}
      </div>

      {/* Two Column Section: Daily Accuracy Trend & Top Forecast Misses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Accuracy Trend */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-900">Daily Accuracy Trend (MAE & RMSE)</h4>
              <p className="text-xs text-slate-500">Daily average error magnitude across January 2026</p>
            </div>
            <Link
              to="/accuracy"
              className="text-xs font-semibold text-electric-600 hover:text-electric-700"
            >
              Full Analytics →
            </Link>
          </div>
          <DailyAccuracyChart data={overview.daily_trend_preview} height={280} />
        </div>

        {/* Top Forecast Misses Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="text-sm font-bold text-slate-900">Largest Forecasting Misses</h4>
                <p className="text-xs text-slate-500">
                  Critical intervals of extreme divergence driving imbalance exposure
                </p>
              </div>
              <span className="text-[10px] uppercase font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                Imbalance Risk
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200/80 text-slate-400 text-[10px] uppercase tracking-wider">
                    <th className="pb-2 font-medium">Delivery Interval</th>
                    <th className="pb-2 font-medium">Forecast</th>
                    <th className="pb-2 font-medium">Actual</th>
                    <th className="pb-2 font-medium">Miss (MW)</th>
                    <th className="pb-2 font-medium">Published</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {overview.top_misses_preview.map((miss, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 font-mono text-slate-800 font-medium">
                        {miss.start_time_utc.slice(5, 16).replace('T', ' ')}
                      </td>
                      <td className="py-2.5 font-mono text-slate-700">{formatMW(miss.forecast_mw)}</td>
                      <td className="py-2.5 font-mono text-slate-700">{formatMW(miss.actual_mw)}</td>
                      <td className="py-2.5 font-mono font-bold text-rose-600">
                        {formatSignedMW(miss.error_mw)}
                      </td>
                      <td className="py-2.5 text-slate-500 text-[11px]">
                        {miss.forecast_age_hours}h lead
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Largest miss: {formatMW(metrics.max_absolute_error_mw)}</span>
            <Link to="/accuracy" className="text-electric-600 font-semibold hover:underline">
              View all extreme intervals
            </Link>
          </div>
        </div>
      </div>

      {/* Procurement Insights Section */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-500" />
          Evidence-Based Procurement Takeaways (January 2026 Analysis)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InsightCard
            category="Systematic Bias"
            title={`Persistent Overforecasting (${formatSignedMW(metrics.bias_mw)})`}
            description="Across January 2026, the available day-ahead wind forecast systematically overestimated actual generation by an average of +1,840 MW. This creates risk of under-procuring baseload or thermal generation."
            impact="Factor in a conservative derating buffer when clearing day-ahead procurement to avoid expensive short imbalance cashout fees."
            icon={TrendingUp}
            variant="amber"
          />

          <InsightCard
            category="Extreme Volatility"
            title={`Peak Error Miss: ${formatMW(metrics.max_absolute_error_mw)}`}
            description="On 12 January 2026 (Settlement Period 3), forecast called for 20,905 MW but actual generation only delivered 14,048 MW. The steep 6.8 GW drop occurred despite forecasts published 15.5 hours in advance."
            impact="Deploy flexible intraday balancing contracts for intervals where forecasted generation exceeds 18 GW."
            icon={AlertCircle}
            variant="blue"
          />

          <InsightCard
            category="Cutoff Governance"
            title="10:00 AM Decision Lead Time"
            description="Evaluating forecasts published strictly prior to 10:00 AM on day D-1 gives procurement teams an average decision lead time of 14–26 hours before physical settlement delivery."
            impact="Enforces strict decision auditability; procurement team never evaluates hindsight forecasts published after trades are committed."
            icon={CheckCircle2}
            variant="teal"
          />
        </div>
      </div>
    </div>
  );
};

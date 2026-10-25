import React, { useState } from 'react';
import {
  Target,
  BarChart3,
  AlertOctagon,
  CheckCircle,
} from 'lucide-react';
import {
  useDailyAccuracy,
  useErrorDistribution,
  useExtremeErrors,
  useDataQuality,
} from '../hooks/useAccuracy';
import { DailyAccuracyChart } from '../components/charts/DailyAccuracyChart';
import { ErrorDistributionChart } from '../components/charts/ErrorDistributionChart';
import { DateRangeFilter } from '../components/common/DateRangeFilter';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { formatMW, formatSignedMW, formatPercent, formatCount } from '../utils/formatters';

export const AccuracyPage: React.FC = () => {
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-31');

  const { data: dailyData, isLoading: isDailyLoading, error: dailyError, refetch: refetchDaily } = useDailyAccuracy({
    start_date: startDate,
    end_date: endDate,
  });

  const { data: distData, isLoading: isDistLoading } = useErrorDistribution({
    start_date: startDate,
    end_date: endDate,
    bins: 12,
  });

  const { data: extremes, isLoading: isExtremesLoading } = useExtremeErrors({
    start_date: startDate,
    end_date: endDate,
    limit: 10,
  });

  const { data: quality } = useDataQuality({
    start_date: startDate,
    end_date: endDate,
  });

  if (isDailyLoading) {
    return <LoadingState message="Calculating statistical accuracy distributions..." />;
  }

  if (dailyError) {
    return <ErrorState message="Failed to calculate accuracy metrics" onRetry={refetchDaily} />;
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Filter */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Quantitative Forecast Accuracy & Distribution
          </h3>
          <p className="text-xs text-slate-500">
            Evaluating error spreads, penalty indicators, and distribution skew for January 2026
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

      {/* Accuracy Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily MAE & RMSE Trends */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <div className="mb-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-electric-600" />
              Daily MAE vs RMSE Trend
            </h4>
            <p className="text-xs text-slate-500">
              When RMSE diverges higher above MAE, it indicates high-magnitude volatile misses on that day
            </p>
          </div>
          {dailyData && dailyData.length > 0 ? (
            <DailyAccuracyChart data={dailyData} height={280} />
          ) : (
            <div className="py-20 text-center text-xs text-slate-400">No data available</div>
          )}
        </div>

        {/* Error Frequency Distribution Histogram */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <div className="mb-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-4 h-4 text-amber-500" />
              Forecast Error Distribution (MW)
            </h4>
            <p className="text-xs text-slate-500">
              Distribution of (Forecast − Actual) across settlement periods. Skew to the right represents overforecasting.
            </p>
          </div>
          {isDistLoading ? (
            <LoadingState className="py-20" />
          ) : distData && distData.length > 0 ? (
            <ErrorDistributionChart data={distData} height={280} />
          ) : (
            <div className="py-20 text-center text-xs text-slate-400">No distribution data</div>
          )}
        </div>
      </div>

      {/* Top 10 Extreme Forecast Errors Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-rose-600" />
              Top 10 Largest Forecast Errors in Evaluation Window
            </h4>
            <p className="text-xs text-slate-500">
              Intervals exhibiting extreme mismatch between 10:00 AM forecast and delivered wind generation
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-rose-50 text-rose-700 border border-rose-200">
            Critical Review
          </span>
        </div>

        {isExtremesLoading ? (
          <LoadingState className="py-20" />
        ) : extremes && extremes.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200/80 text-slate-500 text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4 font-semibold">Delivery Time (UTC)</th>
                  <th className="py-3 px-3 font-semibold">Settlement Period</th>
                  <th className="py-3 px-3 font-semibold">Day-Ahead Forecast</th>
                  <th className="py-3 px-3 font-semibold">Delivered Actual</th>
                  <th className="py-3 px-3 font-semibold">Error (MW)</th>
                  <th className="py-3 px-3 font-semibold">Nature of Miss</th>
                  <th className="py-3 px-4 font-semibold">Selected Forecast Publication</th>
                  <th className="py-3 px-3 font-semibold">Decision Lead</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {extremes.map((record, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">
                      {record.start_time_utc.replace('T', ' ').replace('Z', ' UTC')}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-600">
                      P{record.settlement_period || '—'}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-700 font-bold">
                      {formatMW(record.forecast_mw)}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-700 font-bold">
                      {formatMW(record.actual_mw)}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-rose-600">
                      {formatSignedMW(record.error_mw)}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          record.direction === 'overforecast'
                            ? 'bg-amber-50 text-amber-700 border-amber-200'
                            : 'bg-blue-50 text-blue-700 border-blue-200'
                        }`}
                      >
                        {record.direction === 'overforecast' ? 'Overforecast' : 'Underforecast'}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                      {record.publish_time_utc ? record.publish_time_utc.replace('T', ' ').replace('Z', ' UTC') : '—'}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-500">
                      {record.forecast_age_hours}h lead
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-16 text-center text-xs text-slate-400">No extreme records found</div>
        )}
      </div>

      {/* Data Quality & Completeness Audit Card */}
      {quality && (
        <div className="bg-slate-900 text-white rounded-xl p-5 shadow-xs">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4 border-b border-slate-800 pb-3">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                Data Completeness & Quality Integrity Audit
              </h4>
              <p className="text-xs text-slate-400">
                Transparent verification of all half-hour settlement periods against Elexon source data
              </p>
            </div>
            <span className="text-[11px] font-mono bg-slate-800 px-3 py-1 rounded-md text-slate-300">
              Rule: {quality.decision_cutoff_rule}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 text-[10px] uppercase block mb-1">Expected Periods</span>
              <span className="text-lg font-bold font-mono text-white">
                {formatCount(quality.expected_intervals)}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">48 periods / day</span>
            </div>

            <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 text-[10px] uppercase block mb-1">Actuals Available</span>
              <span className="text-lg font-bold font-mono text-emerald-400">
                {formatCount(quality.available_actual_intervals)}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">100% FUELHH completeness</span>
            </div>

            <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 text-[10px] uppercase block mb-1">Matched Cutoff Intervals</span>
              <span className="text-lg font-bold font-mono text-blue-400">
                {formatCount(quality.matched_intervals)}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">WINDFOR hourly reporting</span>
            </div>

            <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60">
              <span className="text-slate-400 text-[10px] uppercase block mb-1">Coverage Ratio</span>
              <span className="text-lg font-bold font-mono text-white">
                {formatPercent(quality.coverage_percent)}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">0 invented data points</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

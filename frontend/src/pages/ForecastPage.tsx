import React, { useState } from 'react';
import {
  LineChart as LineChartIcon,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useForecastComparison, useForecastTimeseries } from '../hooks/useForecasts';
import { ForecastActualChart } from '../components/charts/ForecastActualChart';
import { ForecastErrorChart } from '../components/charts/ForecastErrorChart';
import { DateRangeFilter } from '../components/common/DateRangeFilter';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { formatMW, formatSignedMW } from '../utils/formatters';

export const ForecastPage: React.FC = () => {
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-07');
  const [page, setPage] = useState(1);
  const perPage = 24;

  const {
    data: paginatedData,
    isLoading,
    error,
    refetch,
  } = useForecastComparison({
    start_date: startDate,
    end_date: endDate,
    page,
    per_page: perPage,
  });

  const { data: timeseries, isLoading: isTimeseriesLoading } = useForecastTimeseries(
    startDate,
    endDate
  );

  const items = paginatedData?.data || [];
  const meta = paginatedData?.meta;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Filter and Info */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Delivery Schedule vs Decision Forecasts
          </h3>
          <p className="text-xs text-slate-500">
            Compare each settlement interval against the forecast available at the 10:00 AM decision cutoff
          </p>
        </div>
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onRangeChange={(start, end) => {
            setStartDate(start);
            setEndDate(end);
            setPage(1);
          }}
        />
      </div>

      {/* Main Interactive Chart Section */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <LineChartIcon className="w-4 h-4 text-electric-600" />
              Generation Profile (MW)
            </h4>
            <p className="text-xs text-slate-500">
              Blue line: Latest forecast before cutoff | Teal line: Actual generation from FUELHH
            </p>
          </div>
          <div className="text-[11px] text-slate-500 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block" /> Forecast
            <span className="w-2.5 h-2.5 rounded-full bg-teal-600 inline-block ml-2" /> Actual
          </div>
        </div>

        {isTimeseriesLoading ? (
          <LoadingState className="py-24" message="Loading timeseries generation data..." />
        ) : timeseries && timeseries.length > 0 ? (
          <ForecastActualChart data={timeseries} height={360} />
        ) : (
          <EmptyState />
        )}
      </div>

      {/* Forecast Error Spreads Area Chart */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
        <div className="mb-4">
          <h4 className="text-sm font-bold text-slate-900">
            Forecast Error Deviations (Forecast − Actual)
          </h4>
          <p className="text-xs text-slate-500">
            Values above 0 MW indicate overforecasting; values below 0 MW indicate underforecasting
          </p>
        </div>
        {isTimeseriesLoading ? (
          <LoadingState className="py-16" />
        ) : timeseries && timeseries.length > 0 ? (
          <ForecastErrorChart data={timeseries} height={240} />
        ) : (
          <EmptyState />
        )}
      </div>

      {/* Granular Matched Records Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-slate-900">Interval Matching Ledger</h4>
            <p className="text-xs text-slate-500">
              Each row shows the exact forecast published prior to cutoff matched with physical settlement
            </p>
          </div>
          {meta && (
            <div className="text-xs text-slate-500">
              Showing {(page - 1) * perPage + 1}–{Math.min(page * perPage, meta.total)} of{' '}
              <span className="font-semibold text-slate-800">{meta.total}</span> intervals
            </div>
          )}
        </div>

        {isLoading ? (
          <LoadingState className="py-20" />
        ) : error ? (
          <ErrorState onRetry={refetch} />
        ) : items.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200/80 text-slate-500 text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4 font-semibold">Delivery Time (UTC)</th>
                  <th className="py-3 px-3 font-semibold">Settlement Period</th>
                  <th className="py-3 px-3 font-semibold">Selected Forecast</th>
                  <th className="py-3 px-3 font-semibold">Actual Generation</th>
                  <th className="py-3 px-3 font-semibold">Error (MW)</th>
                  <th className="py-3 px-3 font-semibold">Direction</th>
                  <th className="py-3 px-4 font-semibold">Forecast Published</th>
                  <th className="py-3 px-3 font-semibold">Forecast Age</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {items.map((item, idx) => {
                  const isOver = item.error > 0;
                  return (
                    <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-mono font-medium text-slate-900">
                        {item.start_time_utc.replace('T', ' ').replace('Z', ' UTC')}
                      </td>
                      <td className="py-3 px-3 text-slate-600 font-mono">
                        P{item.settlement_period || '—'}
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-blue-700">
                        {formatMW(item.forecast_mw)}
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-teal-700">
                        {formatMW(item.actual_mw)}
                      </td>
                      <td className="py-3 px-3 font-mono font-bold">
                        <span className={isOver ? 'text-amber-600' : 'text-blue-600'}>
                          {formatSignedMW(item.error)}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                            isOver
                              ? 'bg-amber-50 text-amber-700 border-amber-200'
                              : 'bg-blue-50 text-blue-700 border-blue-200'
                          }`}
                        >
                          {isOver ? 'Overforecast' : 'Underforecast'}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                        {item.publish_time_utc ? item.publish_time_utc.replace('T', ' ').replace('Z', ' UTC') : '—'}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-500">
                        {item.forecast_age_hours}h lead
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {meta && meta.total_pages > 1 && (
          <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
            <div>
              Page <span className="font-semibold text-slate-800">{page}</span> of{' '}
              <span className="font-semibold text-slate-800">{meta.total_pages}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={!meta.has_prev}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-slate-700 transition-colors"
              >
                <ChevronLeft className="w-3.5 h-3.5" /> Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!meta.has_next}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-slate-700 transition-colors"
              >
                Next <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { MatchedForecastItem } from '../../types/forecast';
import { formatMW, formatSignedMW } from '../../utils/formatters';

interface ForecastActualChartProps {
  data: MatchedForecastItem[];
  height?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const item: MatchedForecastItem = payload[0].payload;
    return (
      <div className="bg-navy-950/95 backdrop-blur-xs text-white p-3 rounded-lg shadow-xl border border-slate-700 text-xs max-w-xs">
        <p className="font-semibold text-slate-200 mb-1.5 border-b border-slate-800 pb-1">
          {label} (Settlement P{item.settlement_period || '—'})
        </p>
        <div className="space-y-1">
          <div className="flex justify-between gap-4">
            <span className="text-electric-400 font-medium">Selected Forecast:</span>
            <span className="font-mono font-bold">{formatMW(item.forecast_mw)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-teal-400 font-medium">Actual Generation:</span>
            <span className="font-mono font-bold">{formatMW(item.actual_mw)}</span>
          </div>
          <div className="flex justify-between gap-4 pt-1 border-t border-slate-800">
            <span className="text-slate-400">Forecast Error:</span>
            <span
              className={`font-mono font-bold ${
                item.error > 0 ? 'text-amber-400' : item.error < 0 ? 'text-blue-400' : 'text-slate-300'
              }`}
            >
              {formatSignedMW(item.error)}
            </span>
          </div>
          <div className="text-[10px] text-slate-400 pt-1">
            <span>Published: </span>
            <span className="text-slate-300">{item.publish_time_utc?.replace('T', ' ').replace('Z', ' UTC')}</span>
            <span className="ml-1 text-slate-500">({item.forecast_age_hours}h lead)</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

export const ForecastActualChart: React.FC<ForecastActualChartProps> = ({ data, height = 360 }) => {
  const chartData = data.map((d) => ({
    ...d,
    formattedTime: d.start_time_utc.slice(5, 16).replace('T', ' '),
  }));

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 15, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="formattedTime"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            interval="preserveStartEnd"
            minTickGap={45}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            tickFormatter={(val) => `${(val / 1000).toFixed(0)}k MW`}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ paddingBottom: 12, fontSize: 12 }}
          />
          <Line
            type="monotone"
            dataKey="forecast_mw"
            name="Forecast Generation (at 10:00 cutoff)"
            stroke="#2563EB"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5, stroke: '#2563EB', strokeWidth: 2, fill: '#ffffff' }}
          />
          <Line
            type="monotone"
            dataKey="actual_mw"
            name="Actual Generation (FUELHH WIND)"
            stroke="#0D9488"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5, stroke: '#0D9488', strokeWidth: 2, fill: '#ffffff' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

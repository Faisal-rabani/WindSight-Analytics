import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { DailyAccuracyRecord } from '../../types/analytics';
import { formatMW } from '../../utils/formatters';

interface DailyAccuracyChartProps {
  data: DailyAccuracyRecord[];
  height?: number;
}

const CustomDailyTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const item: DailyAccuracyRecord = payload[0].payload;
    return (
      <div className="bg-navy-950/95 backdrop-blur-xs text-white p-3 rounded-lg shadow-xl border border-slate-700 text-xs">
        <p className="font-semibold text-slate-200 mb-1 border-b border-slate-800 pb-1">
          {item.date}
        </p>
        <div className="space-y-1">
          <div className="flex justify-between gap-4">
            <span className="text-electric-400">Mean Absolute Error (MAE):</span>
            <span className="font-mono font-bold">{formatMW(item.mae_mw)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-indigo-300">Root Mean Square Error (RMSE):</span>
            <span className="font-mono font-bold">{formatMW(item.rmse_mw)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-amber-400">Daily Bias (MBE):</span>
            <span className="font-mono font-bold">
              {item.bias_mw > 0 ? `+${item.bias_mw}` : item.bias_mw} MW
            </span>
          </div>
          <div className="flex justify-between gap-4 pt-1 border-t border-slate-800 text-[10px] text-slate-400">
            <span>Matched Intervals:</span>
            <span>{item.matched_intervals} / {item.expected_intervals} ({item.coverage_percent}%)</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

export const DailyAccuracyChart: React.FC<DailyAccuracyChartProps> = ({ data, height = 300 }) => {
  const chartData = data.map((d) => ({
    ...d,
    shortDate: d.date.slice(8, 10) + ' Jan',
  }));

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 15, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="shortDate" stroke="#94a3b8" fontSize={11} tickLine={false} />
          <YAxis
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            tickFormatter={(val) => `${val} MW`}
          />
          <Tooltip content={<CustomDailyTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ paddingBottom: 10, fontSize: 12 }}
          />
          <Bar
            dataKey="mae_mw"
            name="Daily MAE (Average Error)"
            fill="#3B82F6"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="rmse_mw"
            name="Daily RMSE (Penalizing Large Misses)"
            fill="#1E293B"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

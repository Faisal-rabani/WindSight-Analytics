import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import { MatchedForecastItem } from '../../types/forecast';
import { formatSignedMW } from '../../utils/formatters';

interface ForecastErrorChartProps {
  data: MatchedForecastItem[];
  height?: number;
}

export const ForecastErrorChart: React.FC<ForecastErrorChartProps> = ({ data, height = 280 }) => {
  const chartData = data.map((d) => ({
    ...d,
    formattedTime: d.start_time_utc.slice(5, 16).replace('T', ' '),
  }));

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 15, left: 0, bottom: 0 }}>
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
            tickFormatter={(val) => `${(val / 1000).toFixed(1)}k MW`}
          />
          <Tooltip
            formatter={(value: any) => [formatSignedMW(value), 'Forecast Deviation (Error)']}
            contentStyle={{
              backgroundColor: '#070F1E',
              borderColor: '#334155',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '12px',
            }}
          />
          <ReferenceLine y={0} stroke="#475569" strokeWidth={1.5} />
          <Area
            type="monotone"
            dataKey="error"
            stroke="#2563EB"
            fill="#3B82F6"
            fillOpacity={0.2}
            strokeWidth={1.5}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
} from 'recharts';
import { ErrorBin } from '../../types/analytics';

interface ErrorDistributionChartProps {
  data: ErrorBin[];
  height?: number;
}

export const ErrorDistributionChart: React.FC<ErrorDistributionChartProps> = ({
  data,
  height = 280,
}) => {
  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 15, left: 0, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="label"
            stroke="#94a3b8"
            fontSize={10}
            tickLine={false}
            angle={-20}
            textAnchor="end"
            interval={0}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            tickFormatter={(val) => `${val} periods`}
          />
          <Tooltip
            formatter={(value: any, _name: any, item: any) => [
              `${value} intervals (${item.payload.percentage}%)`,
              'Frequency Count',
            ]}
            contentStyle={{
              backgroundColor: '#070F1E',
              borderColor: '#334155',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '12px',
            }}
          />
          <ReferenceLine y={0} stroke="#94a3b8" />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => {
              // Color negative bins blue (underforecast) and positive bins amber/red (overforecast)
              const isOverforecast = entry.bin_center > 0;
              return (
                <Cell
                  key={`cell-${index}`}
                  fill={isOverforecast ? '#F59E0B' : '#3B82F6'}
                  opacity={0.85}
                />
              );
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

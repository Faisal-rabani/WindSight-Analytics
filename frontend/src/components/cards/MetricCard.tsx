import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant: 'positive' | 'negative' | 'neutral' | 'info';
  };
  details?: { label: string; value: string }[];
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  details,
  className = '',
}) => {
  const badgeStyles = {
    positive: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    negative: 'bg-rose-50 text-rose-700 border-rose-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
  };

  return (
    <div className={`bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs card-hover flex flex-col justify-between ${className}`}>
      <div>
        <div className="flex items-center justify-between gap-3 mb-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
          <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-navy-900">
            <Icon className="w-4 h-4" />
          </div>
        </div>

        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl font-bold text-slate-900 tracking-tight">{value}</span>
          {badge && (
            <span
              className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badgeStyles[badge.variant]}`}
            >
              {badge.text}
            </span>
          )}
        </div>

        {subtitle && <p className="text-xs text-slate-500 leading-relaxed">{subtitle}</p>}
      </div>

      {details && details.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          {details.map((d, idx) => (
            <div key={idx} className="flex flex-col">
              <span className="text-[10px] text-slate-400 uppercase">{d.label}</span>
              <span className="font-semibold text-slate-700">{d.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

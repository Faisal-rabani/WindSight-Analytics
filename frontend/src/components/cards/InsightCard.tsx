import React from 'react';
import { LucideIcon, ArrowUpRight } from 'lucide-react';

interface InsightCardProps {
  title: string;
  category: string;
  description: string;
  impact: string;
  icon: LucideIcon;
  variant?: 'blue' | 'amber' | 'teal';
  className?: string;
}

export const InsightCard: React.FC<InsightCardProps> = ({
  title,
  category,
  description,
  impact,
  icon: Icon,
  variant = 'blue',
  className = '',
}) => {
  const themes = {
    blue: {
      bg: 'bg-blue-50/50 border-blue-200/80',
      iconBg: 'bg-blue-100 text-blue-700',
      tag: 'text-blue-700 bg-blue-100/70',
    },
    amber: {
      bg: 'bg-amber-50/50 border-amber-200/80',
      iconBg: 'bg-amber-100 text-amber-700',
      tag: 'text-amber-800 bg-amber-100/70',
    },
    teal: {
      bg: 'bg-teal-50/50 border-teal-200/80',
      iconBg: 'bg-teal-100 text-teal-700',
      tag: 'text-teal-800 bg-teal-100/70',
    },
  };

  const currentTheme = themes[variant];

  return (
    <div className={`p-4 rounded-xl border ${currentTheme.bg} transition-all card-hover flex flex-col justify-between ${className}`}>
      <div>
        <div className="flex items-center justify-between mb-2.5">
          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${currentTheme.tag}`}>
            {category}
          </span>
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${currentTheme.iconBg}`}>
            <Icon className="w-3.5 h-3.5" />
          </div>
        </div>

        <h4 className="text-sm font-semibold text-slate-900 mb-1">{title}</h4>
        <p className="text-xs text-slate-600 leading-relaxed mb-3">{description}</p>
      </div>

      <div className="pt-2 border-t border-slate-200/60 flex items-center gap-1.5 text-xs font-semibold text-slate-800">
        <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
        <span>Procurement Takeaway: </span>
        <span className="font-normal text-slate-600">{impact}</span>
      </div>
    </div>
  );
};

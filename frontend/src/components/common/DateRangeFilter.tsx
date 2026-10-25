import React from 'react';
import { Calendar, Filter } from 'lucide-react';

interface DateRangeFilterProps {
  startDate: string;
  endDate: string;
  onRangeChange: (start: string, end: string) => void;
  className?: string;
}

export const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  startDate,
  endDate,
  onRangeChange,
  className = '',
}) => {
  const presets = [
    { label: 'Full Jan 2026', start: '2026-01-01', end: '2026-01-31' },
    { label: 'Week 1 (1–7 Jan)', start: '2026-01-01', end: '2026-01-07' },
    { label: 'Week 2 (8–14 Jan)', start: '2026-01-08', end: '2026-01-14' },
    { label: 'Week 3 (15–21 Jan)', start: '2026-01-15', end: '2026-01-21' },
    { label: 'Week 4 (22–31 Jan)', start: '2026-01-22', end: '2026-01-31' },
  ];

  return (
    <div className={`flex flex-wrap items-center gap-3 bg-white px-4 py-2.5 rounded-xl border border-slate-200/80 shadow-sm ${className}`}>
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
        <Filter className="w-3.5 h-3.5 text-electric-600" />
        <span>Analysis Range:</span>
      </div>

      <div className="flex items-center gap-1.5 flex-wrap">
        {presets.map((preset) => {
          const isActive = startDate === preset.start && endDate === preset.end;
          return (
            <button
              key={preset.label}
              onClick={() => onRangeChange(preset.start, preset.end)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg transition-all ${
                isActive
                  ? 'bg-navy-900 text-white shadow-xs font-semibold'
                  : 'bg-slate-100/70 text-slate-600 hover:bg-slate-200/70'
              }`}
            >
              {preset.label}
            </button>
          );
        })}
      </div>

      <div className="h-4 w-px bg-slate-200 hidden sm:block" />

      <div className="flex items-center gap-2 text-xs">
        <Calendar className="w-3.5 h-3.5 text-slate-400" />
        <input
          type="date"
          value={startDate}
          min="2026-01-01"
          max="2026-02-01"
          onChange={(e) => onRangeChange(e.target.value, endDate)}
          className="border border-slate-200 rounded-md px-2 py-0.5 text-slate-700 text-xs focus:ring-1 focus:ring-electric-500 focus:outline-none"
        />
        <span className="text-slate-400">to</span>
        <input
          type="date"
          value={endDate}
          min="2026-01-01"
          max="2026-02-01"
          onChange={(e) => onRangeChange(startDate, e.target.value)}
          className="border border-slate-200 rounded-md px-2 py-0.5 text-slate-700 text-xs focus:ring-1 focus:ring-electric-500 focus:outline-none"
        />
      </div>
    </div>
  );
};

import { Clock, Globe } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="bg-white border-b border-slate-200/80 px-8 py-4.5 flex flex-wrap items-center justify-between gap-4 shrink-0 shadow-2xs">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-slate-900">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        {/* Pilot Parameters Badges */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200/80 text-xs text-slate-700">
          <Clock className="w-3.5 h-3.5 text-electric-600" />
          <span className="font-semibold text-slate-800">Cutoff: 10:00 AM UK</span>
          <span className="text-slate-400 text-[10px]">(Day-1)</span>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200/80 text-xs text-slate-700">
          <Globe className="w-3.5 h-3.5 text-teal-600" />
          <span className="font-semibold text-slate-800">Europe/London</span>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Elexon BMRS Verified</span>
        </div>
      </div>
    </header>
  );
};

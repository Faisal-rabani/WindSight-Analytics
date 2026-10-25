import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  LineChart,
  Target,
  BookOpen,
  Wind,
  ShieldCheck,
  Zap,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    {
      to: '/',
      label: 'Overview',
      icon: LayoutDashboard,
      description: 'Executive KPIs & Summary',
    },
    {
      to: '/forecasts',
      label: 'Wind Forecasts',
      icon: LineChart,
      description: 'Forecast vs Actual Comparison',
    },
    {
      to: '/accuracy',
      label: 'Accuracy Analysis',
      icon: Target,
      description: 'MAE, RMSE & Error Spreads',
    },
    {
      to: '/methodology',
      label: 'Methodology',
      icon: BookOpen,
      description: 'Cutoff Logic & Assumptions',
    },
  ];

  return (
    <aside className="w-64 bg-navy-950 text-white flex flex-col justify-between shrink-0 border-r border-slate-800">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-electric-600 flex items-center justify-center text-white shadow-md shadow-electric-600/30">
              <Wind className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
                WindForecast <span className="text-electric-400 font-mono text-xs">UK</span>
              </h1>
              <p className="text-[11px] text-slate-400">Power Procurement Intel</p>
            </div>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-2 text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
            Decision Analytics
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-electric-600 text-white shadow-sm font-semibold'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                }`
              }
            >
              <item.icon className="w-4 h-4 shrink-0" />
              <div>
                <div>{item.label}</div>
                <div className="text-[10px] opacity-75 font-normal">{item.description}</div>
              </div>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Pilot Status */}
      <div className="p-4 m-3 rounded-xl bg-slate-900/90 border border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-1.5">
          <ShieldCheck className="w-4 h-4" />
          <span>Verified Elexon Data</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-snug">
          Evaluated at <span className="text-white font-medium">10:00 AM UK</span> previous-day decision cutoff.
        </p>
        <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>Scope: Jan 2026</span>
          <span className="flex items-center gap-1 text-electric-400">
            <Zap className="w-3 h-3" /> Live Pilot
          </span>
        </div>
      </div>
    </aside>
  );
};

import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const DashboardLayout: React.FC = () => {
  const location = useLocation();

  const getPageMeta = (pathname: string) => {
    switch (pathname) {
      case '/':
        return {
          title: 'Executive Forecast Intelligence',
          subtitle: 'Day-ahead wholesale procurement wind forecast evaluation for January 2026',
        };
      case '/forecasts':
        return {
          title: 'Wind Forecast Comparison',
          subtitle: 'Granular half-hourly delivery intervals matched against 10:00 AM decision-time forecasts',
        };
      case '/accuracy':
        return {
          title: 'Forecast Accuracy & Error Intelligence',
          subtitle: 'Quantitative MAE, RMSE, systematic bias analysis, and error distributions',
        };
      case '/methodology':
        return {
          title: 'Methodology & Technical Specifications',
          subtitle: 'Decision-time cutoff algorithms, Elexon datasets, metric formulations, and governance',
        };
      default:
        return {
          title: 'UK Wind Power Forecast Intelligence',
          subtitle: 'Energy utility analytics platform',
        };
    }
  };

  const meta = getPageMeta(location.pathname);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header title={meta.title} subtitle={meta.subtitle} />
        <main className="flex-1 overflow-y-auto px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

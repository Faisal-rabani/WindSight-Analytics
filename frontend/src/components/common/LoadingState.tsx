import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading intelligence metrics...',
  className = 'py-16',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center ${className}`}>
      <div className="relative mb-4">
        <div className="w-12 h-12 rounded-full border-4 border-slate-200 border-t-electric-600 animate-spin" />
        <Loader2 className="w-6 h-6 text-electric-600 absolute inset-0 m-auto animate-pulse" />
      </div>
      <p className="text-sm font-medium text-slate-600">{message}</p>
      <span className="text-xs text-slate-400 mt-1">Analyzing Elexon BMRS settlement records</span>
    </div>
  );
};

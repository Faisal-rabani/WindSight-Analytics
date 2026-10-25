/**
 * Formats a number to MW representation with commas (e.g., 14,250 MW).
 */
export function formatMW(val: number | null | undefined, decimals: number = 0): string {
  if (val === null || val === undefined || isNaN(val)) return '— MW';
  return `${val.toLocaleString('en-GB', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })} MW`;
}

/**
 * Formats a signed error value (e.g., +1,450 MW or -850 MW).
 */
export function formatSignedMW(val: number | null | undefined, decimals: number = 0): string {
  if (val === null || val === undefined || isNaN(val)) return '— MW';
  const prefix = val > 0 ? '+' : '';
  return `${prefix}${val.toLocaleString('en-GB', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })} MW`;
}

/**
 * Formats a percentage (e.g., 98.5%).
 */
export function formatPercent(val: number | null | undefined, decimals: number = 1): string {
  if (val === null || val === undefined || isNaN(val)) return '—%';
  return `${val.toFixed(decimals)}%`;
}

/**
 * Formats integer count with commas.
 */
export function formatCount(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return val.toLocaleString('en-GB');
}

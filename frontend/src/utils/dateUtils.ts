import { format, parseISO, isValid } from 'date-fns';

/**
 * Formats ISO timestamp to concise UK display (e.g. 15 Jan 14:00).
 */
export function formatDateTime(isoStr: string | null | undefined): string {
  if (!isoStr) return '—';
  try {
    const dt = parseISO(isoStr);
    return isValid(dt) ? format(dt, 'dd MMM yyyy, HH:mm') : isoStr;
  } catch {
    return isoStr;
  }
}

/**
 * Formats ISO timestamp to short time (e.g. 14:00).
 */
export function formatTimeOnly(isoStr: string | null | undefined): string {
  if (!isoStr) return '—';
  try {
    const dt = parseISO(isoStr);
    return isValid(dt) ? format(dt, 'HH:mm') : isoStr;
  } catch {
    return isoStr;
  }
}

/**
 * Formats date string to concise format (e.g. 15 Jan 2026).
 */
export function formatDateOnly(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  try {
    const dt = parseISO(dateStr);
    return isValid(dt) ? format(dt, 'dd MMM yyyy') : dateStr;
  } catch {
    return dateStr;
  }
}

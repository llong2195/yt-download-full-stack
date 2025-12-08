/**
 * History API client functions
 */

import { fetchApi } from './api';
import type { HistoryListResponse, HistoryStatsResponse } from '../types/download';

export interface HistoryFilters {
  search?: string;
  date_from?: string;
  date_to?: string;
  success?: boolean;
  limit?: number;
  offset?: number;
}

/**
 * Fetch download history with optional filters
 */
export async function fetchHistory(filters: HistoryFilters = {}): Promise<HistoryListResponse> {
  const params = new URLSearchParams();
  
  if (filters.search) params.append('search', filters.search);
  if (filters.date_from) params.append('date_from', filters.date_from);
  if (filters.date_to) params.append('date_to', filters.date_to);
  if (filters.success !== undefined) params.append('success', String(filters.success));
  if (filters.limit) params.append('limit', String(filters.limit));
  if (filters.offset) params.append('offset', String(filters.offset));

  const queryString = params.toString();
  const url = queryString ? `/api/history?${queryString}` : '/api/history';
  
  return fetchApi<HistoryListResponse>(url, {
    method: 'GET',
  });
}

/**
 * Fetch history statistics for a given period
 */
export async function fetchHistoryStats(period: '7d' | '30d' | '90d' | 'all' = 'all'): Promise<HistoryStatsResponse> {
  return fetchApi<HistoryStatsResponse>(`/api/history/stats?period=${period}`, {
    method: 'GET',
  });
}

/**
 * History page - Browse download history with search and filters
 */

import { useState, useEffect } from 'react';
import { HistoryItem } from '../components/HistoryItem';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { 
  History as HistoryIcon, 
  Search, 
  Filter, 
  Download, 
  CheckCircle2, 
  AlertCircle,
  HardDrive,
  Clock,
  RefreshCw,
} from 'lucide-react';
import { fetchHistory, fetchHistoryStats, type HistoryFilters } from '../services/historyApi';
import type { DownloadHistory, HistoryStatsResponse } from '../types/download';
import { formatFileSize } from '../utils/formatters';

export default function History() {
  const [history, setHistory] = useState<DownloadHistory[]>([]);
  const [stats, setStats] = useState<HistoryStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  
  // Filters
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [successFilter, setSuccessFilter] = useState<boolean | undefined>(undefined);
  const [period, setPeriod] = useState<'7d' | '30d' | '90d' | 'all'>('all');
  
  // Pagination
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [limit] = useState(50);

  // Fetch history with filters
  const loadHistory = async (newOffset: number = 0) => {
    setIsLoading(true);
    setError('');
    
    try {
      const filters: HistoryFilters = {
        limit,
        offset: newOffset,
      };
      
      if (search) filters.search = search;
      if (dateFrom) filters.date_from = dateFrom;
      if (dateTo) filters.date_to = dateTo;
      if (successFilter !== undefined) filters.success = successFilter;
      
      const response = await fetchHistory(filters);
      setHistory(response.history);
      setTotal(response.total);
      setOffset(newOffset);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch history';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch stats
  const loadStats = async () => {
    try {
      const statsData = await fetchHistoryStats(period);
      setStats(statsData);
    } catch (err: unknown) {
      console.error('Failed to fetch stats:', err);
    }
  };

  // Initial load
  useEffect(() => {
    loadHistory();
    loadStats();
  }, []);

  // Reload when filters change
  useEffect(() => {
    if (!isLoading) {
      loadHistory(0);
    }
  }, [search, dateFrom, dateTo, successFilter]);

  // Reload stats when period changes
  useEffect(() => {
    loadStats();
  }, [period]);

  // Handle search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Load more (pagination)
  const handleLoadMore = () => {
    loadHistory(offset + limit);
  };

  // Clear filters
  const handleClearFilters = () => {
    setSearchInput('');
    setSearch('');
    setDateFrom('');
    setDateTo('');
    setSuccessFilter(undefined);
  };

  const hasFilters = search || dateFrom || dateTo || successFilter !== undefined;
  const hasMore = offset + limit < total;

  return (
    <div className="container mx-auto py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <HistoryIcon className="h-8 w-8" />
          Download History
        </h1>
        <p className="text-muted-foreground">
          Browse your complete download history with search and filters
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Statistics</h2>
            <div className="flex gap-2">
              {(['7d', '30d', '90d', 'all'] as const).map((p) => (
                <Button
                  key={p}
                  variant={period === p ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPeriod(p)}
                >
                  {p === 'all' ? 'All Time' : p}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription className="flex items-center gap-2">
                  <Download className="h-4 w-4 text-blue-600" />
                  Total Downloads
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.total}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {stats.successful} successful
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  Success Rate
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.success_rate}%</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-purple-600" />
                  Total Size
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{formatFileSize(stats.total_size)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-orange-600" />
                  Avg Download Time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.avg_download_time}s</div>
                {stats.most_downloaded_channel && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Top: {stats.most_downloaded_channel}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="text-sm font-medium mb-2 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search video titles..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Date From */}
            <div>
              <label className="text-sm font-medium mb-2 block">From Date</label>
              <Input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>

            {/* Date To */}
            <div>
              <label className="text-sm font-medium mb-2 block">To Date</label>
              <Input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-4 mt-4">
            {/* Success Filter */}
            <div className="flex gap-2">
              <Button
                variant={successFilter === undefined ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSuccessFilter(undefined)}
              >
                All
              </Button>
              <Button
                variant={successFilter === true ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSuccessFilter(true)}
              >
                <CheckCircle2 className="h-4 w-4 mr-1" />
                Success
              </Button>
              <Button
                variant={successFilter === false ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSuccessFilter(false)}
              >
                <AlertCircle className="h-4 w-4 mr-1" />
                Failed
              </Button>
            </div>

            {/* Clear Filters */}
            {hasFilters && (
              <Button variant="ghost" size="sm" onClick={handleClearFilters}>
                Clear Filters
              </Button>
            )}

            {/* Results Count */}
            <div className="ml-auto text-sm text-muted-foreground">
              Showing {history.length} of {total} records
            </div>
          </div>
        </CardContent>
      </Card>

      {/* History List */}
      <Card>
        <CardHeader>
          <CardTitle>Download History</CardTitle>
          <CardDescription>
            {hasFilters && (
              <Badge variant="outline" className="mr-2">
                Filtered
              </Badge>
            )}
            {total} record(s) found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && history.length === 0 ? (
            <div className="text-center py-12">
              <RefreshCw className="h-12 w-12 mx-auto mb-3 animate-spin text-muted-foreground" />
              <p className="text-muted-foreground">Loading history...</p>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <HistoryIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No download history found</p>
              {hasFilters && (
                <p className="text-sm mt-1">Try adjusting your filters</p>
              )}
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {history.map((item) => (
                  <HistoryItem key={item.id} history={item} />
                ))}
              </div>

              {/* Load More */}
              {hasMore && (
                <div className="mt-6 text-center">
                  <Button
                    variant="outline"
                    onClick={handleLoadMore}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      `Load More (${total - offset - limit} remaining)`
                    )}
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

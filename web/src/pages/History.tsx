/**
 * History page - Browse download history with search and filters
 */

import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Download,
  Filter,
  HardDrive,
  History as HistoryIcon,
  RefreshCw,
  Search,
} from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { HistoryItem } from '../components/HistoryItem';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { fetchChannels } from '../services/channelApi';
import { fetchHistory, fetchHistoryStats, type HistoryFilters } from '../services/historyApi';
import type { Channel } from '../types/channel';
import type { DownloadHistory, HistoryStatsResponse } from '../types/download';
import { formatFileSize } from '../utils/formatters';

export default function History() {
  const [history, setHistory] = useState<DownloadHistory[]>([]);
  const [stats, setStats] = useState<HistoryStatsResponse | null>(null);
  const [channels, setChannels] = useState<Channel[]>([]);
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
  const [, setOffset] = useState(0);
  const [limit] = useState(50);
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch history with filters
  const loadHistory = useCallback(async (newOffset: number = 0) => {
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
  }, [dateFrom, dateTo, limit, search, successFilter]);
  
  // Fetch stats
  const loadStats = useCallback(async () => {
    try {
      const statsData = await fetchHistoryStats(period);
      setStats(statsData);
    } catch (err: unknown) {
      console.error('Failed to fetch stats:', err);
    }
  }, [period]);

  // Load channels for settings display
  const loadChannels = useCallback(async () => {
    try {
      const response = await fetchChannels();
      setChannels(response.channels);
    } catch (err) {
      console.error('Failed to load channels:', err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadHistory();
    loadStats();
    loadChannels();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // // Reload when filters change
  // useEffect(() => {
  //   if (!isLoading) {
  //     loadHistory(0);
  //   }
  // }, [isLoading, loadHistory]);

  // Reload stats when period changes
  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // Handle search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchInput]);


  // Clear filters
  const handleClearFilters = () => {
    setSearchInput('');
    setSearch('');
    setDateFrom('');
    setDateTo('');
    setSuccessFilter(undefined);
  };

  const handleApplyFilters = () => {
    setCurrentPage(1); // Reset to the first page
    loadHistory(0); // Fetch data with updated filters
  };

  const handlePageChange = (page: number) => {
    const newOffset = (page - 1) * limit;
    setCurrentPage(page);
    loadHistory(newOffset);
  };

  const hasFilters = search || dateFrom || dateTo || successFilter !== undefined;
 

  return (
    <div className="mx-auto py-6 sm:py-8 px-4 max-w-6xl">
      {/* Header */}
      <div className="mb-8 space-y-2">
        <h1 className="text-3xl sm:text-4xl font-bold flex items-center gap-3 bg-linear-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
          <div className="rounded-lg bg-primary p-2">
            <HistoryIcon className="h-6 w-6 sm:h-7 sm:w-7 text-primary-foreground" />
          </div>
          Download History
        </h1>
        <p className="text-base text-muted-foreground">
          Browse your complete download history with search and filters
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <h2 className="text-xl font-semibold">Statistics</h2>
            <div className="flex flex-wrap gap-2">
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
                <div className="text-3xl font-bold">{stats.total_downloads}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {stats.successful_downloads} successful
                </div>
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
                <div className="text-3xl font-bold">{formatFileSize(stats.total_size_bytes)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-orange-600" />
                  Avg Download Time
                </CardDescription>
              </CardHeader> 
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
      <Card className="mb-6 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Filter className="h-5 w-5 text-primary" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="text-sm font-medium mb-2 block">Search Videos</label>
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

      {/* Filters Section */}
      <div className="flex items-center gap-4 mb-4">
        <Button onClick={handleApplyFilters} className="bg-primary text-white">
          Apply Filters
        </Button>
      </div>

      {/* History List */}
      <Card className="border-primary/20">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="text-xl">Download History</CardTitle>
              <CardDescription className="mt-1">
                {hasFilters && (
                  <Badge variant="outline" className="mr-2">
                    Filtered
                  </Badge>
                )}
                {total} record(s) found
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading && history.length === 0 ? (
            <div className="text-center py-16">
              <RefreshCw className="h-12 w-12 mx-auto mb-3 animate-spin text-primary" />
              <p className="text-muted-foreground">Loading history...</p>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-16">
              <div className="rounded-full bg-muted p-6 w-fit mx-auto mb-4">
                <HistoryIcon className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No download history found</h3>
              {hasFilters && (
                <p className="text-sm text-muted-foreground mt-1">Try adjusting your filters</p>
              )}
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {history.map((item) => {
                  const channel = channels.find((ch) => ch.id === item.channel_id);
                  return (
                    <HistoryItem 
                      key={item.id} 
                      history={item} 
                      channelName={channel?.name}
                      subtitleLanguage={channel?.subtitle_language}
                      videoQuality={channel?.video_quality}
                    />
                  );
                })}
              </div>
              {/* Loading Indicator */}
              {isLoading && (
                <div className="text-center py-4">
                  <span>Loading...</span>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Pagination Controls */}
      <div className="flex justify-center items-center gap-2 mt-4">
        {Array.from({ length: Math.ceil(total / limit) }, (_, index) => (
          <Button
            key={index}
            onClick={() => handlePageChange(index + 1)}
            className={`px-3 py-1 ${currentPage === index + 1 ? 'bg-primary text-white' : 'bg-gray-200'}`}
          >
            {index + 1}
          </Button>
        ))}
      </div>
    </div>
  );
}

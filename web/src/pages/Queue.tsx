/**
 * Queue page - Monitor active downloads with real-time updates
 */

import { useState, useEffect } from 'react';
import { QueueItem } from '../components/QueueItem';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { RefreshCw, Download, AlertCircle, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { fetchQueueStatus, retryTask } from '../services/downloadApi';
import type { QueueStatusResponse, DownloadTask } from '../types/download';
import { fetchChannels } from '../services/channelApi';
import type { Channel } from '../types/channel';
import { cancelTask } from '../services/queueApi';

const POLL_INTERVAL = 2500; // 2.5 seconds

export default function Queue() {
  const [queueData, setQueueData] = useState<QueueStatusResponse | null>(null);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [retryingTasks, setRetryingTasks] = useState<Set<string>>(new Set());
  const [cancellingTasks, setCancellingTasks] = useState<Set<string>>(new Set());

  // Fetch queue status
  const fetchQueue = async () => {
    try {
      const data = await fetchQueueStatus();
      setQueueData(data);
      setLastUpdated(new Date());
      setError('');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch queue status';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle retry task
  const handleRetry = async (taskId: string) => {
    setRetryingTasks((prev) => new Set(prev).add(taskId));
    
    try {
      await retryTask(taskId);
      // Refresh queue immediately after retry
      await fetchQueue();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to retry task';
      setError(message);
    } finally {
      setRetryingTasks((prev) => {
        const next = new Set(prev);
        next.delete(taskId);
        return next;
      });
    }
  };

  // Handle cancel task
  const handleCancel = async (taskId: string) => {
    setCancellingTasks((prev) => new Set(prev).add(taskId));
    
    try {
      await cancelTask(taskId);
      // Refresh queue immediately after cancel
      await fetchQueue();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to cancel task';
      setError(message);
    } finally {
      setCancellingTasks((prev) => {
        const next = new Set(prev);
        next.delete(taskId);
        return next;
      });
    }
  };

  // Load channels for settings display
  const loadChannels = async () => {
    try {
      const response = await fetchChannels();
      setChannels(response.channels);
    } catch (err) {
      console.error('Failed to load channels:', err);
    }
  };

  // Polling effect
  useEffect(() => {
    fetchQueue(); // Initial fetch
    loadChannels(); // Load channels once

    const intervalId = setInterval(() => {
      fetchQueue();
    }, POLL_INTERVAL);

    // Cleanup on unmount
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  // Manual refresh
  const handleRefresh = () => {
    setIsLoading(true);
    fetchQueue();
  };

  if (isLoading && !queueData) {
    return (
      <div className="mx-auto py-8 max-w-6xl">
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          <span className="ml-2 text-muted-foreground">Loading queue...</span>
        </div>
      </div>
    );
  }

  const stats = queueData
    ? [
        { label: 'Pending', value: queueData.total_pending, icon: Clock, color: 'text-yellow-600' },
        { label: 'Downloading', value: queueData.total_downloading, icon: Download, color: 'text-blue-600' },
        { label: 'Completed Today', value: queueData.total_completed, icon: CheckCircle2, color: 'text-green-600' },
        { label: 'Failed Today', value: queueData.total_failed, icon: XCircle, color: 'text-red-600' },
      ]
    : [];

  return (
    <div className="mx-auto py-6 sm:py-8 px-4 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl font-bold flex items-center gap-3 bg-linear-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              <div className="rounded-lg bg-primary p-2">
                <Download className="h-6 w-6 sm:h-7 sm:w-7 text-primary-foreground" />
              </div>
              Download Queue
            </h1>
            <p className="text-base text-muted-foreground">
              Monitor active downloads and view real-time progress
            </p>
          </div>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <CardDescription className="flex items-center gap-2 text-xs font-medium">
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                  {stat.label}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-xs text-muted-foreground mb-4 flex items-center gap-2">
          <RefreshCw className="h-3 w-3" />
          Last updated: {lastUpdated.toLocaleTimeString()}
          <Badge variant="outline" className="ml-2">
            Auto-refresh every {POLL_INTERVAL / 1000}s
          </Badge>
        </div>
      )}

      {/* Active Tasks */}
      <Card className="border-primary/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">Active Tasks</CardTitle>
              <CardDescription className="mt-1">
                {queueData?.active_tasks.length || 0} task(s) in progress
              </CardDescription>
            </div>
            {queueData && queueData.active_tasks.length > 0 && (
              <Badge variant="secondary" className="text-base px-3 py-1">
                {queueData.active_tasks.length}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {!queueData || queueData.active_tasks.length === 0 ? (
            <div className="text-center py-16">
              <div className="rounded-full bg-muted p-6 w-fit mx-auto mb-4">
                <Download className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No active downloads</h3>
              <p className="text-sm text-muted-foreground">Start downloads from the Downloads page</p>
            </div>
          ) : (
            <div className="space-y-3">
              {queueData.active_tasks.map((task: DownloadTask) => {
                const channel = channels.find((ch) => ch.id === task.channel_id);
                return (
                  <QueueItem
                    key={task.id}
                    task={task}
                    channelName={channel?.name}
                    subtitleLanguage={channel?.subtitle_language}
                    videoQuality={channel?.video_quality}
                    onRetry={handleRetry}
                    isRetrying={retryingTasks.has(task.task_id)}
                    onCancel={handleCancel}
                    isCancelling={cancellingTasks.has(task.task_id)}
                  />
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

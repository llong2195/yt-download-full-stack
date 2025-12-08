/**
 * QueueItem component - Display individual download task with status
 */

import type { DownloadTask } from '../types/download';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { RefreshCw, AlertCircle } from 'lucide-react';

interface QueueItemProps {
  task: DownloadTask;
  channelName?: string;
  onRetry?: (taskId: string) => void;
  isRetrying?: boolean;
}

/**
 * Get badge variant based on task status
 */
function getStatusBadgeVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'pending':
      return 'secondary';
    case 'downloading':
      return 'default';
    case 'completed':
      return 'outline';
    case 'failed':
      return 'destructive';
    default:
      return 'secondary';
  }
}

/**
 * Get color class for status badge
 */
function getStatusColorClass(status: string): string {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300';
    case 'downloading':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300';
    case 'completed':
      return 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300';
    case 'failed':
      return 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300';
    default:
      return '';
  }
}

export function QueueItem({ task, channelName, onRetry, isRetrying = false }: QueueItemProps) {
  const showProgress = task.status === 'downloading';
  const canRetry = task.status === 'failed' && task.retry_count < 3;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base font-mono truncate">
              {task.video_id}
            </CardTitle>
            {channelName && (
              <CardDescription className="text-sm mt-1">
                Channel: {channelName}
              </CardDescription>
            )}
          </div>
          <Badge 
            variant={getStatusBadgeVariant(task.status)}
            className={getStatusColorClass(task.status)}
          >
            {task.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Video URL */}
        <div className="text-xs text-muted-foreground truncate">
          {task.video_url}
        </div>

        {/* Progress Bar */}
        {showProgress && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Downloading...</span>
              <span>{task.progress_percent}%</span>
            </div>
            <Progress value={task.progress_percent} className="h-2" />
          </div>
        )}

        {/* Error Message */}
        {task.status === 'failed' && task.error_message && (
          <div className="flex items-start gap-2 p-2 bg-red-50 dark:bg-red-950/20 rounded text-xs text-red-800 dark:text-red-300">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <span className="flex-1">{task.error_message}</span>
          </div>
        )}

        {/* Task Metadata */}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="space-y-1">
            <div>Task ID: {task.task_id.slice(0, 8)}...</div>
            {task.retry_count > 0 && (
              <div>Retry: {task.retry_count}/3</div>
            )}
          </div>

          {/* Retry Button */}
          {canRetry && onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onRetry(task.task_id)}
              disabled={isRetrying}
            >
              {isRetrying ? (
                <>
                  <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                  Retrying...
                </>
              ) : (
                <>
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Retry
                </>
              )}
            </Button>
          )}
        </div>

        {/* Timestamps */}
        <div className="text-xs text-muted-foreground space-y-1">
          {task.created_at && (
            <div>Created: {new Date(task.created_at).toLocaleString()}</div>
          )}
          {task.started_at && (
            <div>Started: {new Date(task.started_at).toLocaleString()}</div>
          )}
          {task.completed_at && (
            <div>Completed: {new Date(task.completed_at).toLocaleString()}</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

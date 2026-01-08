/**
 * QueueItem component - Display individual download task with status
 */

import { AlertCircle, RefreshCw, Languages, Video, X } from 'lucide-react';
import type { DownloadTask } from '../types/download';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';

interface QueueItemProps {
  task: DownloadTask;
  channelName?: string;
  subtitleLanguage?: string;
  videoQuality?: string;
  onRetry?: (taskId: string) => void;
  onCancel?: (taskId: string) => void;
  isRetrying?: boolean;
  isCancelling?: boolean;
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

export function QueueItem({ task, channelName, subtitleLanguage, videoQuality, onRetry, onCancel, isRetrying = false, isCancelling = false }: QueueItemProps) {
  const showProgress = task.status === 'downloading';
  const canRetry = task.status === 'failed' && task.retry_count < 3;
  const canCancel = task.status !== 'completed';

  return (
    <Card className="hover:shadow-md transition-shadow border-l-4" style={{
      borderLeftColor: task.status === 'downloading' ? 'hsl(var(--primary))' : 
                       task.status === 'completed' ? 'hsl(142, 76%, 36%)' :
                       task.status === 'failed' ? 'hsl(var(--destructive))' :
                       'hsl(var(--muted))'
    }}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base font-mono truncate">
              {task.video_id}
            </CardTitle>
            <CardDescription className="text-sm mt-1 flex flex-wrap items-center gap-2">
              {channelName && (
                <span>Channel: {channelName}</span>
              )}
              {subtitleLanguage && (
                <Badge variant="secondary" className="text-xs">
                  <Languages className="h-3 w-3 mr-1" />
                  {subtitleLanguage.toUpperCase()}
                </Badge>
              )}
              {videoQuality && (
                <Badge variant="secondary" className="text-xs">
                  <Video className="h-3 w-3 mr-1" />
                  {videoQuality}
                </Badge>
              )}
            </CardDescription>
          </div>
          <Badge 
            variant={getStatusBadgeVariant(task.status)}
            className={`${getStatusColorClass(task.status)} shrink-0`}
          >
            {task.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Video URL */}
        <div className="text-xs text-muted-foreground truncate font-mono bg-muted/50 px-2 py-1 rounded">
          {task.video_url}
        </div>

        {/* Progress Bar */}
        {showProgress && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span className="text-primary">Downloading...</span>
              <span className="text-primary">{task.progress_percent}%</span>
            </div>
            <Progress value={task.progress_percent} className="h-2.5" />
          </div>
        )}

        {/* Error Message */}
        {task.status === 'failed' && task.error_message && (
          <Alert variant="destructive" className="py-2">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              {task.error_message}
            </AlertDescription>
          </Alert>
        )}

        {/* Task Metadata & Actions */}
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="font-mono">ID: {task.task_id.slice(0, 12)}...</div>
            {task.retry_count > 0 && (
              <div className="flex items-center gap-1">
                <span className="font-medium">Retry:</span>
                <Badge variant="outline" className="text-xs px-1 py-0">
                  {task.retry_count}/3
                </Badge>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Cancel Button */}
            {canCancel && onCancel && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onCancel(task.task_id)}
                disabled={isCancelling}
                className="text-destructive hover:text-destructive"
              >
                {isCancelling ? (
                  <>
                    <RefreshCw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                    Cancelling...
                  </>
                ) : (
                  <>
                    <X className="h-3.5 w-3.5 mr-1.5" />
                    Cancel
                  </>
                )}
              </Button>
            )}

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
                    <RefreshCw className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                    Retrying...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
                    Retry
                  </>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Timestamps */}
        <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
          {task.created_at && (
            <div><span className="font-medium">Created:</span> {new Date(task.created_at).toLocaleString()}</div>
          )}
          {task.started_at && (
            <div><span className="font-medium">Started:</span> {new Date(task.started_at).toLocaleString()}</div>
          )}
          {task.completed_at && (
            <div><span className="font-medium">Completed:</span> {new Date(task.completed_at).toLocaleString()}</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * History Item component - Display individual download history record
 */

import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { CheckCircle2, XCircle, Calendar, HardDrive, Clock, Download, AlertCircle } from 'lucide-react';
import type { DownloadHistory } from '../types/download';

interface HistoryItemProps {
  history: DownloadHistory;
  channelName?: string;
}

/**
 * Format file size to human-readable format
 */
function formatFileSize(bytes: number | null): string {
  if (!bytes) return 'N/A';
  
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

/**
 * Format duration to HH:MM:SS or MM:SS
 */
function formatDuration(seconds: number | null): string {
  if (!seconds) return 'N/A';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format date to locale string
 */
function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleString();
}

export function HistoryItem({ history, channelName }: HistoryItemProps) {
  const StatusIcon = history.success ? CheckCircle2 : XCircle;
  const statusColor = history.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
  const badgeVariant = history.success ? 'default' : 'destructive';
  const borderColor = history.success ? 'border-l-green-500' : 'border-l-red-500';

  return (
    <Card className={`hover:shadow-md transition-shadow border-l-4 ${borderColor}`}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base line-clamp-2 group-hover:text-primary transition-colors">
              {history.video_title}
            </CardTitle>
            <CardDescription className="mt-2 flex flex-wrap items-center gap-2">
              {channelName && (
                <Badge variant="outline" className="text-xs">
                  {channelName}
                </Badge>
              )}
              <span className="text-xs text-muted-foreground font-mono">
                {history.video_id}
              </span>
            </CardDescription>
          </div>
          <Badge variant={badgeVariant} className="shrink-0">
            <StatusIcon className="h-3 w-3 mr-1" />
            {history.success ? 'Success' : 'Failed'}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {/* Download Date */}
          <div className="flex items-start gap-2">
            <Calendar className={`h-4 w-4 ${statusColor} mt-0.5`} />
            <div>
              <div className="text-xs text-muted-foreground font-medium">Downloaded</div>
              <div className="text-xs mt-0.5">{formatDate(history.download_date)}</div>
            </div>
          </div>

          {/* File Size */}
          <div className="flex items-start gap-2">
            <HardDrive className={`h-4 w-4 ${statusColor} mt-0.5`} />
            <div>
              <div className="text-xs text-muted-foreground font-medium">File Size</div>
              <div className="font-medium">{formatFileSize(history.file_size ?? null)}</div>
            </div>
          </div>

          {/* Duration */}
          <div className="flex items-start gap-2">
            <Clock className={`h-4 w-4 ${statusColor} mt-0.5`} />
            <div>
              <div className="text-xs text-muted-foreground font-medium">Duration</div>
              <div className="text-xs mt-0.5 font-mono">{formatDuration(history.duration ?? null)}</div>
            </div>
          </div>

          {/* Download Time */}
          <div className="flex items-start gap-2">
            <Download className={`h-4 w-4 ${statusColor} mt-0.5`} />
            <div>
              <div className="text-xs text-muted-foreground font-medium">Download Time</div>
              <div className="text-xs mt-0.5 font-mono">
                {history.download_duration_seconds 
                  ? `${history.download_duration_seconds}s` 
                  : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Error Code (if failed) */}
        {!history.success && history.error_code && (
          <Alert variant="destructive" className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              <span className="font-semibold">Error Code: </span>
              {history.error_code}
            </AlertDescription>
          </Alert>
        )}

        {/* File Path */}
        {history.file_path && (
          <div className="mt-4 p-3 bg-muted/50 rounded-lg">
            <div className="text-xs text-muted-foreground font-medium mb-1">File Path</div>
            <code className="text-xs break-all">{history.file_path}</code>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

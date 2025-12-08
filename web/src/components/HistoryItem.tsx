/**
 * History Item component - Display individual download history record
 */

import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { CheckCircle2, XCircle, Calendar, HardDrive, Clock } from 'lucide-react';
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
  const statusColor = history.success ? 'text-green-600' : 'text-red-600';
  const badgeVariant = history.success ? 'default' : 'destructive';

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base line-clamp-2">
              {history.video_title}
            </CardTitle>
            <CardDescription className="mt-1 flex items-center gap-2">
              {channelName && (
                <span className="text-sm">{channelName}</span>
              )}
              <span className="text-xs text-muted-foreground">
                ID: {history.video_id}
              </span>
            </CardDescription>
          </div>
          <Badge variant={badgeVariant} className="ml-2">
            <StatusIcon className="h-3 w-3 mr-1" />
            {history.success ? 'Success' : 'Failed'}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {/* Download Date */}
          <div className="flex items-center gap-2">
            <Calendar className={`h-4 w-4 ${statusColor}`} />
            <div>
              <div className="text-xs text-muted-foreground">Downloaded</div>
              <div className="font-medium">{formatDate(history.download_date)}</div>
            </div>
          </div>

          {/* File Size */}
          <div className="flex items-center gap-2">
            <HardDrive className={`h-4 w-4 ${statusColor}`} />
            <div>
              <div className="text-xs text-muted-foreground">File Size</div>
              <div className="font-medium">{formatFileSize(history.file_size ?? null)}</div>
            </div>
          </div>

          {/* Duration */}
          <div className="flex items-center gap-2">
            <Clock className={`h-4 w-4 ${statusColor}`} />
            <div>
              <div className="text-xs text-muted-foreground">Duration</div>
              <div className="font-medium">{formatDuration(history.duration ?? null)}</div>
            </div>
          </div>

          {/* Download Time */}
          <div className="flex items-center gap-2">
            <Clock className={`h-4 w-4 ${statusColor}`} />
            <div>
              <div className="text-xs text-muted-foreground">Download Time</div>
              <div className="font-medium">
                {history.download_duration_seconds 
                  ? `${history.download_duration_seconds}s` 
                  : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Error Code (if failed) */}
        {!history.success && history.error_code && (
          <div className="mt-3 p-2 bg-destructive/10 border border-destructive/20 rounded text-xs">
            <span className="font-semibold">Error: </span>
            {history.error_code}
          </div>
        )}

        {/* File Path */}
        {history.file_path && (
          <div className="mt-3 text-xs text-muted-foreground">
            <span className="font-semibold">Path: </span>
            <code className="bg-muted px-1 py-0.5 rounded">{history.file_path}</code>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * TypeScript types for download-related entities and API requests/responses.
 * These match the backend Pydantic schemas in models/schemas.py
 */

// ============================================================================
// Download Task Types
// ============================================================================

export interface DownloadTask {
  id: number;
  task_id: string;
  channel_id: number;
  video_id: string;
  video_url: string;
  status: "pending" | "downloading" | "completed" | "failed";
  progress_percent: number;
  error_message?: string;
  retry_count: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

// ============================================================================
// Download History Types
// ============================================================================

export interface DownloadHistory {
  id: number;
  channel_id: number;
  video_id: string;
  video_title: string;
  video_url: string;
  task_id?: string;
  download_date: string;
  upload_date?: string;
  duration?: number; // in seconds
  file_path?: string;
  file_size?: number; // in bytes
  video_metadata?: string; // JSON string
  download_duration_seconds: number;
  success: boolean;
  error_code?: string;
}

// ============================================================================
// Request Types
// ============================================================================

export interface DownloadRequest {
  video_url: string;
  channel_id: number;
}

export interface BatchUrlDownloadRequest {
  video_urls: string[];
}

// ============================================================================
// Response Types
// ============================================================================

export interface BatchDownloadResponse {
  tasks: DownloadTask[];
  total_requested: number;
  total_created: number;
  total_skipped: number;
  skipped_reason?: string;
}

export interface QueueStatusResponse {
  total_pending: number;
  total_downloading: number;
  total_completed: number;
  total_failed: number;
  active_tasks: DownloadTask[];
}

export interface TaskRetryResponse {
  success: boolean;
  new_task_id: string;
  message: string;
}

export interface HistoryListResponse {
  history: DownloadHistory[];
  total: number;
  page: number;
  page_size: number;
}

export interface HistoryStatsResponse {
  total_downloads: number;
  successful_downloads: number;
  failed_downloads: number;
  total_size_bytes: number;
  total_duration_seconds: number;
  average_download_time_seconds: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ErrorResponse {
  error_code: string;
  message: string;
  details?: string;
}

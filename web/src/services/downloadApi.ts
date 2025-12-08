/**
 * API client for download-related endpoints
 */

import { fetchApi } from "./api";
import type {
  DownloadRequest,
  BatchUrlDownloadRequest,
  DownloadTask,
  BatchDownloadResponse,
  QueueStatusResponse,
  TaskRetryResponse,
  HistoryListResponse,
  HistoryStatsResponse,
} from "../types/download";

const DOWNLOADS_BASE = "/api/downloads";
const QUEUE_BASE = "/api/queue";
const HISTORY_BASE = "/api/history";

// ============================================================================
// Download Endpoints
// ============================================================================

/**
 * Request a single video download
 */
export async function requestSingleDownload(
  request: DownloadRequest
): Promise<DownloadTask> {
  return fetchApi<DownloadTask>(DOWNLOADS_BASE, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * Request batch download by URLs with auto-channel detection
 */
export async function requestBatchDownloadByUrls(
  videoUrls: string[]
): Promise<BatchDownloadResponse> {
  const request: BatchUrlDownloadRequest = { video_urls: videoUrls };
  return fetchApi<BatchDownloadResponse>(`${DOWNLOADS_BASE}/batch-urls`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

// ============================================================================
// Queue Endpoints
// ============================================================================

/**
 * Fetch current queue status with active tasks
 */
export async function fetchQueueStatus(): Promise<QueueStatusResponse> {
  return fetchApi<QueueStatusResponse>(`${QUEUE_BASE}/status`);
}

/**
 * Fetch single task status by task_id
 */
export async function fetchTaskStatus(taskId: string): Promise<DownloadTask> {
  return fetchApi<DownloadTask>(`${QUEUE_BASE}/tasks/${taskId}`);
}

/**
 * Retry a failed task
 */
export async function retryTask(taskId: string): Promise<TaskRetryResponse> {
  return fetchApi<TaskRetryResponse>(`${QUEUE_BASE}/tasks/${taskId}/retry`, {
    method: "POST",
  });
}

// ============================================================================
// History Endpoints
// ============================================================================

/**
 * Fetch download history with pagination
 */
export async function fetchHistory(
  page: number = 1,
  pageSize: number = 20,
  channelId?: number,
  searchQuery?: string
): Promise<HistoryListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (channelId) {
    params.append("channel_id", channelId.toString());
  }

  if (searchQuery) {
    params.append("search", searchQuery);
  }

  return fetchApi<HistoryListResponse>(`${HISTORY_BASE}?${params.toString()}`);
}

/**
 * Fetch download statistics
 */
export async function fetchHistoryStats(
  channelId?: number
): Promise<HistoryStatsResponse> {
  const params = channelId
    ? new URLSearchParams({ channel_id: channelId.toString() })
    : "";
  const url = params
    ? `${HISTORY_BASE}/stats?${params}`
    : `${HISTORY_BASE}/stats`;
  return fetchApi<HistoryStatsResponse>(url);
}

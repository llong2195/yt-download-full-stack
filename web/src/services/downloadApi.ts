/**
 * API client for download-related endpoints
 */

import type {
  BatchDownloadResponse,
  BatchUrlDownloadRequest,
  DownloadRequest,
  DownloadTask,
  QueueStatusResponse,
  TaskRetryResponse
} from "../types/download";
import { fetchApi } from "./api";

const DOWNLOADS_BASE = "/downloads";
const QUEUE_BASE = "/queue";

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

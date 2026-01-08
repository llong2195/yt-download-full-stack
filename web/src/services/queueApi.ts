/**
 * Queue API service - Functions for queue management
 */

import { fetchApi } from './api';

export interface CancelTaskResponse {
  success: boolean;
  message: string;
  task_id: string;
}

/**
 * Cancel/delete a task from queue
 */
export async function cancelTask(taskId: string): Promise<CancelTaskResponse> {
  return fetchApi<CancelTaskResponse>(`/queue/tasks/${taskId}`, {
    method: 'DELETE',
  });
}

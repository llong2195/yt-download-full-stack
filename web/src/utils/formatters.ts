/**
 * Utility formatters for displaying data
 */

/**
 * Format file size to human-readable format
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes || bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

/**
 * Format duration in seconds to HH:MM:SS or MM:SS
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (!seconds || seconds === 0) return '0:00';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format ISO date string to locale string
 */
export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return 'N/A';
  
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Format ISO date string to date only (no time)
 */
export function formatDateOnly(isoString: string | null | undefined): string {
  if (!isoString) return 'N/A';
  
  try {
    return new Date(isoString).toLocaleDateString();
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Format ISO date string to time only (no date)
 */
export function formatTimeOnly(isoString: string | null | undefined): string {
  if (!isoString) return 'N/A';
  
  try {
    return new Date(isoString).toLocaleTimeString();
  } catch {
    return 'Invalid Time';
  }
}

/**
 * Global settings types
 */

export interface GlobalSettings {
  id: number;
  default_download_path: string;
  default_subtitle_language?: string;
  default_video_quality?: string;
  created_at: string;
  updated_at?: string;
}

export interface GlobalSettingsUpdateRequest {
  default_download_path: string;
  default_subtitle_language?: string;
  default_video_quality?: string;
}

// Re-export constants from channel types for convenience
import { VALID_LANGUAGES, VALID_QUALITIES } from './channel';
export { VALID_LANGUAGES, VALID_QUALITIES };

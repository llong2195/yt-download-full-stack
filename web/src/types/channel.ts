/**
 * Channel entity types
 */

export interface Channel {
  id: number;
  channel_id: string;
  title: string; // YouTube channel title
  name: string; // Custom user-defined name
  url: string;
  download_path: string;
  subtitle_language?: string;
  video_quality?: string;
  date_added: string;
  last_updated?: string;
  video_count?: number; // Only present in list responses
}

export interface ChannelCreateRequest {
  url: string;
  name: string; // Custom channel name (required)
  download_path?: string;
  subtitle_language?: string;
  video_quality?: string;
}

export interface ChannelUpdateRequest {
  name?: string;
  download_path?: string;
  subtitle_language?: string;
  video_quality?: string;
}

export interface ChannelListResponse {
  channels: Channel[];
  total: number;
}

export interface ChannelImportRequest {
  raw_text: string;
}

export interface ChannelImportResult {
  line_number: number;
  name: string;
  url: string;
  status: "created" | "updated" | "failed";
  channel_id?: number;
  error?: string;
}

export interface ChannelImportResponse {
  results: ChannelImportResult[];
  total: number;
  created: number;
  updated: number;
  failed: number;
}

export interface ErrorResponse {
  detail: string;
}

// Valid subtitle language codes (ISO 639-1)
export const VALID_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'zh', name: 'Chinese' },
  { code: 'vi', name: 'Vietnamese' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'ru', name: 'Russian' },
  { code: 'ar', name: 'Arabic' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'it', name: 'Italian' },
  { code: 'th', name: 'Thai' },
  { code: 'pl', name: 'Polish' },
  { code: 'nl', name: 'Dutch' },
] as const;

// Valid video quality settings
export const VALID_QUALITIES = [
  { code: 'best', name: 'Best Available' },
  { code: '2160p', name: '4K (2160p)' },
  { code: '1440p', name: 'QHD (1440p)' },
  { code: '1080p', name: 'Full HD (1080p)' },
  { code: '720p', name: 'HD (720p)' },
  { code: '480p', name: 'SD (480p)' },
  { code: '360p', name: '360p' },
  { code: '240p', name: '240p' },
  { code: '144p', name: '144p' },
] as const;

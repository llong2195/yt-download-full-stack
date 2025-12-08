/**
 * Channel entity types
 */

export interface Channel {
  id: number;
  channel_id: string;
  name: string;
  url: string;
  download_path: string;
  date_added: string;
  last_updated?: string;
  video_count?: number; // Only present in list responses
}

export interface ChannelCreateRequest {
  url: string;
}

export interface ChannelListResponse {
  channels: Channel[];
  total: number;
}

export interface ErrorResponse {
  detail: string;
}

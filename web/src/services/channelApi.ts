/**
 * Channel API client
 */

import { fetchApi } from "./api";
import type {
  Channel,
  ChannelCreateRequest,
  ChannelUpdateRequest,
  ChannelListResponse,
} from "@/types/channel";

export async function fetchChannels(): Promise<ChannelListResponse> {
  return fetchApi<ChannelListResponse>("/channels");
}

export async function addChannel(
  request: ChannelCreateRequest
): Promise<Channel> {
  return fetchApi<Channel>("/channels", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function updateChannel(
  channelId: number,
  request: ChannelUpdateRequest
): Promise<Channel> {
  return fetchApi<Channel>(`/channels/${channelId}`, {
    method: "PUT",
    body: JSON.stringify(request),
  });
}

export async function deleteChannel(channelId: number): Promise<void> {
  return fetchApi<void>(`/channels/${channelId}`, {
    method: "DELETE",
  });
}

/**
 * Channel API client
 */

import { fetchApi } from "./api";
import type {
  Channel,
  ChannelCreateRequest,
  ChannelListResponse,
} from "@/types/channel";

export async function fetchChannels(): Promise<ChannelListResponse> {
  return fetchApi<ChannelListResponse>("/channels");
}

export async function addChannel(url: string): Promise<Channel> {
  return fetchApi<Channel>("/channels", {
    method: "POST",
    body: JSON.stringify({ url } as ChannelCreateRequest),
  });
}

export async function deleteChannel(channelId: number): Promise<void> {
  return fetchApi<void>(`/channels/${channelId}`, {
    method: "DELETE",
  });
}

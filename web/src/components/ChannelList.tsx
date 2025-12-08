/**
 * ChannelList component - renders list of channel cards
 */

import type { Channel } from "@/types/channel";
import ChannelCard from "./ChannelCard";

interface ChannelListProps {
  channels: Channel[];
  onDeleteChannel: (channelId: number) => void;
  deletingId?: number;
}

export default function ChannelList({
  channels,
  onDeleteChannel,
  deletingId,
}: ChannelListProps) {
  if (channels.length === 0) {
    return (
      <div className="empty-state">
        <p>No channels yet. Add a YouTube channel to get started!</p>
      </div>
    );
  }

  return (
    <div className="channel-list">
      {channels.map((channel) => (
        <ChannelCard
          key={channel.id}
          channel={channel}
          onDelete={onDeleteChannel}
          isDeleting={deletingId === channel.id}
        />
      ))}
    </div>
  );
}

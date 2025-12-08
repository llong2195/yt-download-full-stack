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
      <div className="flex items-center justify-center py-12 text-center">
        <div className="space-y-2">
          <p className="text-muted-foreground">No channels yet.</p>
          <p className="text-sm text-muted-foreground">
            Add a YouTube channel to get started!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
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

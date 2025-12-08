/**
 * ChannelCard component - displays a single channel with actions
 */

import type { Channel } from "@/types/channel";

interface ChannelCardProps {
  channel: Channel;
  onDelete: (channelId: number) => void;
  isDeleting?: boolean;
}

export default function ChannelCard({
  channel,
  onDelete,
  isDeleting = false,
}: ChannelCardProps) {
  return (
    <div className="channel-card">
      <div className="channel-header">
        <h3>{channel.name}</h3>
        <button
          onClick={() => onDelete(channel.id)}
          disabled={isDeleting}
          className="delete-button"
          aria-label="Delete channel"
        >
          {isDeleting ? "..." : "×"}
        </button>
      </div>

      <div className="channel-info">
        <p className="channel-url">
          <a href={channel.url} target="_blank" rel="noopener noreferrer">
            {channel.url}
          </a>
        </p>

        <div className="channel-meta">
          <span>Videos: {channel.video_count || 0}</span>
          <span>•</span>
          <span>
            Added: {new Date(channel.date_added).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

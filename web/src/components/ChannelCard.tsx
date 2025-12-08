/**
 * ChannelCard component - displays a single channel with actions
 */

import { Trash2, ExternalLink } from "lucide-react";
import type { Channel } from "@/types/channel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-xl font-semibold">
            {channel.name}
          </CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDelete(channel.id)}
            disabled={isDeleting}
            className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <a
          href={channel.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-primary hover:underline break-all"
        >
          <ExternalLink className="h-3 w-3 shrink-0" />
          {channel.url}
        </a>
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span>Videos: {channel.video_count || 0}</span>
          <span>•</span>
          <span>
            Added: {new Date(channel.date_added).toLocaleDateString()}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

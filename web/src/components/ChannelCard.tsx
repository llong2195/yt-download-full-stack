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
    <Card className="group hover:shadow-lg transition-all duration-200 hover:border-primary/50">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold truncate group-hover:text-primary transition-colors">
              {channel.name}
            </CardTitle>
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <span className="inline-flex items-center px-2 py-1 rounded-full bg-primary/10 text-primary font-medium">
                {channel.video_count || 0} videos
              </span>
              <span>•</span>
              <span>
                {new Date(channel.date_added).toLocaleDateString()}
              </span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDelete(channel.id)}
            disabled={isDeleting}
            className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 shrink-0"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <a
          href={channel.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-sm text-primary hover:underline break-all group/link"
        >
          <ExternalLink className="h-3.5 w-3.5 shrink-0 group-hover/link:translate-x-0.5 transition-transform" />
          <span className="truncate">{channel.url}</span>
        </a>
      </CardContent>
    </Card>
  );
}

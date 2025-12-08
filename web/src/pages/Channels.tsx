/**
 * Channels page - main UI for channel management
 */

import { useState, useEffect } from "react";
import { Plus, RefreshCw } from "lucide-react";
import type { Channel } from "@/types/channel";
import {
  fetchChannels,
  addChannel,
  deleteChannel,
} from "@/services/channelApi";
import { ApiError } from "@/services/api";
import ChannelList from "@/components/ChannelList";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function Channels() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  // Add channel form state
  const [newChannelUrl, setNewChannelUrl] = useState("");
  const [addingChannel, setAddingChannel] = useState(false);
  const [addError, setAddError] = useState<string>("");

  // Delete state
  const [deletingId, setDeletingId] = useState<number>();

  // Load channels on mount
  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await fetchChannels();
      setChannels(response.channels);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to load channels";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddChannel = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newChannelUrl.trim()) {
      setAddError("Please enter a YouTube channel URL");
      return;
    }

    try {
      setAddingChannel(true);
      setAddError("");

      const newChannel = await addChannel(newChannelUrl.trim());

      // Add to list with video_count = 0
      setChannels([{ ...newChannel, video_count: 0 }, ...channels]);

      // Clear form
      setNewChannelUrl("");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to add channel";
      setAddError(message);
    } finally {
      setAddingChannel(false);
    }
  };

  const handleDeleteChannel = async (channelId: number) => {
    if (
      !confirm(
        "Are you sure you want to delete this channel? This will also remove all associated downloads."
      )
    ) {
      return;
    }

    try {
      setDeletingId(channelId);
      await deleteChannel(channelId);

      // Remove from list
      setChannels(channels.filter((ch) => ch.id !== channelId));
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to delete channel";
      alert(`Error: ${message}`);
    } finally {
      setDeletingId(undefined);
    }
  };

  return (
    <div className="mx-auto py-6 sm:py-8 px-4 max-w-7xl">
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight bg-linear-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            YouTube Channels
          </h1>
          <p className="text-base text-muted-foreground">
            Manage the YouTube channels you want to download from
          </p>
        </div>

        {/* Add Channel Form */}
        <Card className="border-primary/20 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5 text-primary" />
              Add New Channel
            </CardTitle>
            <CardDescription>
              Enter a YouTube channel URL to start downloading videos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAddChannel} className="flex flex-col sm:flex-row gap-3">
              <Input
                type="text"
                placeholder="https://www.youtube.com/@channel or https://youtube.com/@username"
                value={newChannelUrl}
                onChange={(e) => setNewChannelUrl(e.target.value)}
                disabled={addingChannel}
                className="flex-1"
              />
              <Button type="submit" disabled={addingChannel} className="sm:w-auto w-full">
                {addingChannel ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Channel
                  </>
                )}
              </Button>
            </form>

            {addError && (
              <Alert variant="destructive" className="mt-4">
                <AlertDescription>{addError}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Channel List */}
        <div>
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <RefreshCw className="h-8 w-8 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">
                Loading channels...
              </span>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <span>{error}</span>
                <Button variant="outline" size="sm" onClick={loadChannels}>
                  Retry
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {!loading && !error && channels.length === 0 && (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <div className="rounded-full bg-muted p-4 mb-4">
                  <Plus className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No channels yet</h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  Add your first YouTube channel above to start downloading videos
                </p>
              </CardContent>
            </Card>
          )}

          {!loading && !error && channels.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">
                  Your Channels ({channels.length})
                </h2>
              </div>
              <ChannelList
                channels={channels}
                onDeleteChannel={handleDeleteChannel}
                deletingId={deletingId}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

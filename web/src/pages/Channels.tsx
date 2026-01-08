/**
 * Channels page - main UI for channel management
 */

import ChannelImportDialog from "@/components/ChannelImportDialog";
import ChannelList from "@/components/ChannelList";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/services/api";
import {
  addChannel,
  deleteChannel,
  fetchChannels,
  updateChannel,
} from "@/services/channelApi";
import type { Channel } from "@/types/channel";
import { FolderOpen, Plus, RefreshCw, Upload } from "lucide-react";
import { useEffect, useState } from "react";

export default function Channels() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  // Add channel form state
  const [newChannelUrl, setNewChannelUrl] = useState("");
  const [newChannelName, setNewChannelName] = useState("");
  const [newChannelPath, setNewChannelPath] = useState("");
  const [newChannelLanguage, setNewChannelLanguage] = useState("");
  const [newChannelQuality, setNewChannelQuality] = useState("");
  const [addingChannel, setAddingChannel] = useState(false);
  const [addError, setAddError] = useState<string>("");

  // Delete state
  const [deletingId, setDeletingId] = useState<number>();

  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null);
  const [editName, setEditName] = useState("");
  const [editPath, setEditPath] = useState("");
  const [editLanguage, setEditLanguage] = useState("");
  const [editQuality, setEditQuality] = useState("");
  const [updatingChannel, setUpdatingChannel] = useState(false);
  const [editError, setEditError] = useState<string>("");

  // Import dialog state
  const [importDialogOpen, setImportDialogOpen] = useState(false);

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

    if (!newChannelName.trim()) {
      setAddError("Please enter a custom channel name");
      return;
    }

    try {
      setAddingChannel(true);
      setAddError("");

      const newChannel = await addChannel({
        url: newChannelUrl.trim(),
        name: newChannelName.trim(),
        download_path: newChannelPath.trim() || undefined,
        subtitle_language: newChannelLanguage || undefined,
        video_quality: newChannelQuality || undefined,
      });

      // Add to list with video_count = 0
      setChannels([{ ...newChannel, video_count: 0 }, ...channels]);

      // Clear form
      setNewChannelUrl("");
      setNewChannelName("");
      setNewChannelPath("");
      setNewChannelLanguage("");
      setNewChannelQuality("");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to add channel";
      setAddError(message);
    } finally {
      setAddingChannel(false);
    }
  };

  const handleEditChannel = (channel: Channel) => {
    setEditingChannel(channel);
    setEditName(channel.name);
    setEditPath(channel.download_path || "");
    setEditLanguage(channel.subtitle_language || "");
    setEditQuality(channel.video_quality || "");
    setEditError("");
    setEditDialogOpen(true);
  };

  const handleUpdateChannel = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!editingChannel) return;

    if (!editName.trim()) {
      setEditError("Please enter a custom channel name");
      return;
    }

    try {
      setUpdatingChannel(true);
      setEditError("");

      const updated = await updateChannel(editingChannel.id, {
        name: editName.trim(),
        download_path: editPath.trim() || undefined,
        subtitle_language: editLanguage || undefined,
        video_quality: editQuality || undefined,
      });

      // Update in list
      setChannels(
        channels.map((ch) =>
          ch.id === editingChannel.id ? { ...ch, ...updated } : ch
        )
      );

      // Close dialog
      setEditDialogOpen(false);
      setEditingChannel(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to update channel";
      setEditError(message);
    } finally {
      setUpdatingChannel(false);
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
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight bg-linear-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              YouTube Channels
            </h1>
            <p className="text-base text-muted-foreground">
              Manage the YouTube channels you want to download from
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="default"
              onClick={() => setImportDialogOpen(true)}
              className="gap-2"
            >
              <Upload className="h-4 w-4" />
              Import Channels
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={loadChannels}
              disabled={loading}
              title="Refresh channels"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
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
            <form onSubmit={handleAddChannel} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2 sm:col-span-2">
                  <label htmlFor="channel-url" className="text-sm font-medium">
                    YouTube Channel URL <span className="text-destructive">*</span>
                  </label>
                  <Input
                    id="channel-url"
                    type="text"
                    placeholder="https://www.youtube.com/@channel"
                    value={newChannelUrl}
                    onChange={(e) => setNewChannelUrl(e.target.value)}
                    disabled={addingChannel}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="channel-name" className="text-sm font-medium">
                    Custom Name <span className="text-destructive">*</span>
                  </label>
                  <Input
                    id="channel-name"
                    type="text"
                    placeholder="My Channel"
                    value={newChannelName}
                    onChange={(e) => setNewChannelName(e.target.value)}
                    disabled={addingChannel}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="download-path" className="text-sm font-medium flex items-center gap-2">
                    <FolderOpen className="h-4 w-4" />
                    Download Path (optional)
                  </label>
                  <Input
                    id="download-path"
                    type="text"
                    placeholder="D:\Downloads\my-channel or ./downloads/my-channel"
                    value={newChannelPath}
                    onChange={(e) => setNewChannelPath(e.target.value)}
                    disabled={addingChannel}
                  />
                  <p className="text-xs text-muted-foreground">
                    Enter absolute path (e.g., D:\Downloads\channel) or relative path (e.g., ./downloads/channel). Leave empty to use default.
                  </p>
                </div>

                <div className="space-y-2">
                  <label htmlFor="subtitle-lang" className="text-sm font-medium">
                    Subtitle Language (optional)
                  </label>
                  <select
                    id="subtitle-lang"
                    value={newChannelLanguage}
                    onChange={(e) => setNewChannelLanguage(e.target.value)}
                    disabled={addingChannel}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="">-- Use Global Default --</option>
                    <option value="en">English</option>
                    <option value="ja">Japanese</option>
                    <option value="ko">Korean</option>
                    <option value="vi">Vietnamese</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label htmlFor="video-quality" className="text-sm font-medium">
                    Video Quality (optional)
                  </label>
                  <select
                    id="video-quality"
                    value={newChannelQuality}
                    onChange={(e) => setNewChannelQuality(e.target.value)}
                    disabled={addingChannel}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="">-- Use Global Default --</option>
                    <option value="best">Best Available</option>
                    <option value="1080p">Full HD (1080p)</option>
                    <option value="720p">HD (720p)</option>
                    <option value="480p">SD (480p)</option>
                    <option value="360p">360p</option>
                  </select>
                </div>
              </div>

              <Button type="submit" disabled={addingChannel} className="w-full sm:w-auto">
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
                onEditChannel={handleEditChannel}
                deletingId={deletingId}
              />
            </div>
          )}
        </div>

        {/* Edit Channel Dialog */}
        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent className="sm:max-w-[525px]">
            <DialogHeader>
              <DialogTitle>Edit Channel</DialogTitle>
              <DialogDescription>
                Update channel name and download settings
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleUpdateChannel} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="edit-name" className="text-sm font-medium">
                  Custom Name <span className="text-destructive">*</span>
                </label>
                <Input
                  id="edit-name"
                  type="text"
                  placeholder="My Channel"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  disabled={updatingChannel}
                  required
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="edit-path" className="text-sm font-medium flex items-center gap-2">
                  <FolderOpen className="h-4 w-4" />
                  Download Path (optional)
                </label>
                <Input
                  id="edit-path"
                  type="text"
                  placeholder="D:\Downloads\my-channel or ./downloads/my-channel"
                  value={editPath}
                  onChange={(e) => setEditPath(e.target.value)}
                  disabled={updatingChannel}
                />
                <p className="text-xs text-muted-foreground">
                  Absolute path (e.g., D:\Downloads\channel) or relative path (e.g., ./downloads/channel)
                </p>
              </div>

              <div className="space-y-2">
                <label htmlFor="edit-language" className="text-sm font-medium">
                  Subtitle Language (optional)
                </label>
                <select
                  id="edit-language"
                  value={editLanguage}
                  onChange={(e) => setEditLanguage(e.target.value)}
                  disabled={updatingChannel}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="">-- Use Global Default --</option>
                  <option value="en">English</option>
                  <option value="ja">Japanese</option>
                  <option value="ko">Korean</option>
                  <option value="vi">Vietnamese</option>
                </select>
              </div>

              <div className="space-y-2">
                <label htmlFor="edit-quality" className="text-sm font-medium">
                  Video Quality (optional)
                </label>
                <select
                  id="edit-quality"
                  value={editQuality}
                  onChange={(e) => setEditQuality(e.target.value)}
                  disabled={updatingChannel}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="">-- Use Global Default --</option>
                  <option value="best">Best Available</option>
                  <option value="1080p">Full HD (1080p)</option>
                  <option value="720p">HD (720p)</option>
                  <option value="480p">SD (480p)</option>
                  <option value="360p">360p</option>
                </select>
              </div>

              <div className="flex justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setEditDialogOpen(false)}
                  disabled={updatingChannel}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={updatingChannel}>
                  {updatingChannel ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    "Save Changes"
                  )}
                </Button>
              </div>

              {editError && (
                <Alert variant="destructive">
                  <AlertDescription>{editError}</AlertDescription>
                </Alert>
              )}
            </form>
          </DialogContent>
        </Dialog>

        {/* Import Dialog */}
        <ChannelImportDialog
          open={importDialogOpen}
          onOpenChange={setImportDialogOpen}
          onImportComplete={loadChannels}
        />
      </div>
    </div>
  );
}

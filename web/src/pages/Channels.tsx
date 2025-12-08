/**
 * Channels page - main UI for channel management
 */

import { useState, useEffect } from "react";
import type { Channel } from "@/types/channel";
import {
  fetchChannels,
  addChannel,
  deleteChannel,
} from "@/services/channelApi";
import { ApiError } from "@/services/api";
import ChannelList from "@/components/ChannelList";
import "./Channels.css";

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
    <div className="channels-page">
      <header className="page-header">
        <h1>YouTube Channels</h1>
        <p>Manage the YouTube channels you want to download from</p>
      </header>

      {/* Add Channel Form */}
      <section className="add-channel-section">
        <form onSubmit={handleAddChannel} className="add-channel-form">
          <input
            type="text"
            placeholder="Enter YouTube channel URL (e.g., https://www.youtube.com/@channel)"
            value={newChannelUrl}
            onChange={(e) => setNewChannelUrl(e.target.value)}
            disabled={addingChannel}
            className="channel-url-input"
          />
          <button type="submit" disabled={addingChannel} className="add-button">
            {addingChannel ? "Adding..." : "Add Channel"}
          </button>
        </form>

        {addError && <div className="error-message">{addError}</div>}
      </section>

      {/* Channel List */}
      <section className="channels-section">
        {loading && <div className="loading">Loading channels...</div>}

        {error && (
          <div className="error-message">
            {error}
            <button onClick={loadChannels}>Retry</button>
          </div>
        )}

        {!loading && !error && (
          <ChannelList
            channels={channels}
            onDeleteChannel={handleDeleteChannel}
            deletingId={deletingId}
          />
        )}
      </section>
    </div>
  );
}

/**
 * Settings page - global download configuration
 */

import { useState, useEffect } from "react";
import { Save, RefreshCw, Settings as SettingsIcon, FolderOpen } from "lucide-react";
import type { GlobalSettings } from "@/types/settings";
import { fetchSettings, updateSettings } from "@/services/settingsApi";
import { ApiError } from "@/services/api";
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

export default function Settings() {
  const [settings, setSettings] = useState<GlobalSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  // Form state
  const [downloadPath, setDownloadPath] = useState("");
  const [subtitleLanguage, setSubtitleLanguage] = useState("");
  const [videoQuality, setVideoQuality] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string>("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  // Update form when settings loaded
  useEffect(() => {
    if (settings) {
      setDownloadPath(settings.default_download_path);
      setSubtitleLanguage(settings.default_subtitle_language || "");
      setVideoQuality(settings.default_video_quality || "");
    }
  }, [settings]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await fetchSettings();
      setSettings(data);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to load settings";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!downloadPath.trim()) {
      setSaveError("Download path is required");
      return;
    }

    try {
      setSaving(true);
      setSaveError("");
      setSaveSuccess(false);

      const updated = await updateSettings({
        default_download_path: downloadPath.trim(),
        default_subtitle_language: subtitleLanguage || undefined,
        default_video_quality: videoQuality || undefined,
      });

      setSettings(updated);
      setSaveSuccess(true);

      // Clear success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to save settings";
      setSaveError(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto py-6 sm:py-8 px-4 max-w-4xl">
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight bg-linear-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            Settings
          </h1>
          <p className="text-base text-muted-foreground">
            Configure global defaults for all channels
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <RefreshCw className="h-8 w-8 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">
              Loading settings...
            </span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <span>{error}</span>
              <Button variant="outline" size="sm" onClick={loadSettings}>
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Settings Form */}
        {!loading && !error && settings && (
          <Card className="border-primary/20 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SettingsIcon className="h-5 w-5 text-primary" />
                Global Defaults
              </CardTitle>
              <CardDescription>
                These settings apply to all channels unless overridden per-channel
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveSettings} className="space-y-6">
                <div className="space-y-2">
                  <label
                    htmlFor="default-download-path"
                    className="text-sm font-medium flex items-center gap-2"
                  >
                    <FolderOpen className="h-4 w-4" />
                    Default Download Path{" "}
                    <span className="text-destructive">*</span>
                  </label>
                  <Input
                    id="default-download-path"
                    type="text"
                    placeholder="D:\Downloads or ./downloads"
                    value={downloadPath}
                    onChange={(e) => setDownloadPath(e.target.value)}
                    disabled={saving}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Base directory where channel folders will be created. Use absolute path (e.g., D:\Downloads) or relative path (e.g., ./downloads)
                  </p>
                </div>

                <div className="grid gap-6 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label
                      htmlFor="default-subtitle-language"
                      className="text-sm font-medium"
                    >
                      Default Subtitle Language
                    </label>
                    <select
                      id="default-subtitle-language"
                      value={subtitleLanguage}
                      onChange={(e) => setSubtitleLanguage(e.target.value)}
                      disabled={saving}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <option value="">-- No Subtitles --</option>
                      <option value="en">English</option>
                      <option value="ja">Japanese</option>
                      <option value="ko">Korean</option>
                      <option value="vi">Vietnamese</option>
                    </select>
                    <p className="text-xs text-muted-foreground">
                      Preferred subtitle language for downloads
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label
                      htmlFor="default-video-quality"
                      className="text-sm font-medium"
                    >
                      Default Video Quality
                    </label>
                    <select
                      id="default-video-quality"
                      value={videoQuality}
                      onChange={(e) => setVideoQuality(e.target.value)}
                      disabled={saving}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <option value="">-- Best Available --</option>
                      <option value="best">Best Available</option>
                      <option value="2160p">4K (2160p)</option>
                      <option value="1440p">QHD (1440p)</option>
                      <option value="1080p">Full HD (1080p)</option>
                      <option value="720p">HD (720p)</option>
                      <option value="480p">SD (480p)</option>
                      <option value="360p">360p</option>
                    </select>
                    <p className="text-xs text-muted-foreground">
                      Preferred video quality for downloads
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-4">
                  <Button type="submit" disabled={saving}>
                    {saving ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Save Settings
                      </>
                    )}
                  </Button>

                  {saveSuccess && (
                    <span className="text-sm text-green-600 dark:text-green-400">
                      ✓ Settings saved successfully
                    </span>
                  )}
                </div>

                {saveError && (
                  <Alert variant="destructive">
                    <AlertDescription>{saveError}</AlertDescription>
                  </Alert>
                )}
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

/**
 * Downloads page - Batch YouTube video download interface
 */

import { useState } from "react";
import { UrlInput } from "../components/UrlInput";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert";
import { Badge } from "../components/ui/badge";
import { CheckCircle2, XCircle, AlertCircle, Download } from "lucide-react";
import { requestBatchDownloadByUrls } from "../services/downloadApi";
import type { BatchDownloadResponse, DownloadTask } from "../types/download";

export default function Downloads() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<BatchDownloadResponse | null>(null);
  const [error, setError] = useState<string>("");

  const handleSubmit = async (urls: string[]) => {
    setIsSubmitting(true);
    setError("");
    setResult(null);

    try {
      const response = await requestBatchDownloadByUrls(urls);
      setResult(response);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to submit download request. Please try again.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto py-6 sm:py-8 px-4 max-w-5xl">
      <div className="mb-8 space-y-3">
        <h1 className="text-3xl sm:text-4xl font-bold flex items-center gap-3 bg-linear-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
          <div className="rounded-lg bg-primary p-2">
            <Download className="h-6 w-6 sm:h-7 sm:w-7 text-primary-foreground" />
          </div>
          Download Videos
        </h1>
        <p className="text-base text-muted-foreground">
          Paste YouTube video URLs below to start downloading. Channels will be created automatically.
        </p>
      </div>

      <Card className="mb-6 border-primary/20 shadow-sm">
        <CardHeader>
          <CardTitle className="text-xl">Batch Download</CardTitle>
          <CardDescription>
            Enter one or more YouTube video URLs (one per line). The system will automatically detect channels, check for duplicates, and queue downloads.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <UrlInput onSubmit={handleSubmit} isLoading={isSubmitting} />
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && (
        <Card className="mb-6 border-green-200 dark:border-green-900 bg-green-50/50 dark:bg-green-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
              <CheckCircle2 className="h-5 w-5" />
              Download Request Submitted
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="text-center p-5 bg-background rounded-lg border shadow-sm">
                <div className="text-3xl font-bold text-primary mb-1">
                  {result.total_requested}
                </div>
                <div className="text-sm font-medium text-muted-foreground">Requested</div>
              </div>
              <div className="text-center p-5 bg-green-500/10 dark:bg-green-500/20 rounded-lg border border-green-200 dark:border-green-800">
                <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
                  {result.total_created}
                </div>
                <div className="text-sm font-medium text-muted-foreground">Queued</div>
              </div>
              <div className="text-center p-5 bg-yellow-500/10 dark:bg-yellow-500/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">
                  {result.total_skipped}
                </div>
                <div className="text-sm font-medium text-muted-foreground">Skipped</div>
              </div>
            </div>

            {/* Skipped Reason */}
            {result.total_skipped > 0 && result.skipped_reason && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{result.skipped_reason}</AlertDescription>
              </Alert>
            )}

            {/* Created Tasks List */}
            {result.tasks.length > 0 && (
              <div>
                <h3 className="font-semibold mb-3">
                  Queued Downloads ({result.tasks.length})
                </h3>
                <div className="space-y-2">
                  {result.tasks.map((task: DownloadTask) => (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-mono text-sm text-muted-foreground">
                          {task.video_id}
                        </div>
                        <div className="text-xs text-muted-foreground truncate">
                          {task.video_url}
                        </div>
                      </div>
                      <Badge
                        variant={
                          task.status === "pending" ? "secondary" : "default"
                        }
                      >
                        {task.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Next Steps</AlertTitle>
              <AlertDescription>
                Your downloads have been queued. Visit the Queue page to monitor
                progress.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

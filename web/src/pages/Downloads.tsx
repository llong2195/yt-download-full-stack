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
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Download className="h-8 w-8" />
          Download Videos
        </h1>
        <p className="text-muted-foreground">
          Paste YouTube video URLs below to start downloading. Channels will be
          created automatically.
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Batch Download</CardTitle>
          <CardDescription>
            Enter one or more YouTube video URLs (one per line). The system will
            automatically detect channels, check for duplicates, and queue
            downloads.
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
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Download Request Submitted
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-primary">
                  {result.total_requested}
                </div>
                <div className="text-sm text-muted-foreground">Requested</div>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {result.total_created}
                </div>
                <div className="text-sm text-muted-foreground">Queued</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {result.total_skipped}
                </div>
                <div className="text-sm text-muted-foreground">Skipped</div>
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

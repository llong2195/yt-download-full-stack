/**
 * Channel Import Dialog Component
 * Allows bulk import of channels from raw text
 */

import { useState } from "react";
import { Upload, FileText, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { importChannels } from "@/services/channelApi";
import type { ChannelImportResponse, ChannelImportResult } from "@/types/channel";

interface ChannelImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImportComplete?: () => void;
}

export default function ChannelImportDialog({
  open,
  onOpenChange,
  onImportComplete,
}: ChannelImportDialogProps) {
  const [rawText, setRawText] = useState("");
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<ChannelImportResponse | null>(null);
  const [error, setError] = useState("");

  const handleImport = async () => {
    if (!rawText.trim()) {
      setError("Please enter channel data to import");
      return;
    }

    try {
      setImporting(true);
      setError("");
      const result = await importChannels(rawText);
      setImportResult(result);
      
      // If import was successful (at least some channels imported), refresh parent
      if (result.created > 0 || result.updated > 0) {
        onImportComplete?.();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to import channels");
    } finally {
      setImporting(false);
    }
  };

  const handleClose = () => {
    setRawText("");
    setImportResult(null);
    setError("");
    onOpenChange(false);
  };

  const getStatusIcon = (status: ChannelImportResult["status"]) => {
    switch (status) {
      case "created":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "updated":
        return <AlertCircle className="h-4 w-4 text-blue-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = (status: ChannelImportResult["status"]) => {
    switch (status) {
      case "created":
        return "Created";
      case "updated":
        return "Updated";
      case "failed":
        return "Failed";
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Bulk Import Channels
          </DialogTitle>
          <DialogDescription>
            Import multiple channels at once. Each line should follow the format:
            <code className="block mt-2 p-2 bg-muted rounded text-xs">
              {`TK004|https://www.youtube.com/@kotaro_|D:\\MMO\\NHẬT\\TK004|ja|1080p`}
            </code>
            Download path is optional. If omitted, the global default will be used.
          </DialogDescription>
        </DialogHeader>

        {!importResult ? (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Channel Data
              </label>
              <Textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder={`Example:\nTK004|https://www.youtube.com/@kotaro_|D:\\MMO\\NHẬT\\TK004|ja|1080p\nTK005|https://www.youtube.com/@ryunarisa|D:\\MMO\\NHẬT\\TK005|ja|1080p|`}
                className="min-h-[300px] font-mono text-sm"
                disabled={importing}
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              <span>
                Lines: {rawText.split('\n').filter(line => line.trim()).length}
              </span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-4 gap-4">
              <div className="p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold">{importResult.total}</div>
                <div className="text-xs text-muted-foreground">Total</div>
              </div>
              <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {importResult.created}
                </div>
                <div className="text-xs text-green-600 dark:text-green-400">Created</div>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {importResult.updated}
                </div>
                <div className="text-xs text-blue-600 dark:text-blue-400">Updated</div>
              </div>
              <div className="p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {importResult.failed}
                </div>
                <div className="text-xs text-red-600 dark:text-red-400">Failed</div>
              </div>
            </div>

            {/* Detailed Results */}
            <div>
              <h4 className="text-sm font-medium mb-2">Import Results</h4>
              <ScrollArea className="h-[300px] border rounded-md">
                <div className="p-4 space-y-2">
                  {importResult.results.map((result, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 rounded-lg bg-muted/50"
                    >
                      <div className="mt-0.5">{getStatusIcon(result.status)}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-muted-foreground">
                            Line {result.line_number}
                          </span>
                          <span className={`text-xs font-medium ${
                            result.status === "created"
                              ? "text-green-600 dark:text-green-400"
                              : result.status === "updated"
                              ? "text-blue-600 dark:text-blue-400"
                              : "text-red-600 dark:text-red-400"
                          }`}>
                            {getStatusText(result.status)}
                          </span>
                        </div>
                        <div className="font-medium truncate">{result.name}</div>
                        <div className="text-xs text-muted-foreground truncate">
                          {result.url}
                        </div>
                        {result.error && (
                          <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                            {result.error}
                          </div>
                        )}
                        {result.channel_id && (
                          <div className="text-xs text-muted-foreground mt-1">
                            Channel ID: {result.channel_id}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>
        )}

        <DialogFooter>
          {!importResult ? (
            <>
              <Button variant="outline" onClick={handleClose} disabled={importing}>
                Cancel
              </Button>
              <Button onClick={handleImport} disabled={importing || !rawText.trim()}>
                {importing ? "Importing..." : "Import Channels"}
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={() => setImportResult(null)}>
                Import More
              </Button>
              <Button onClick={handleClose}>Close</Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

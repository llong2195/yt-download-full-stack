/**
 * UrlInput component for batch YouTube URL submission
 * Allows users to paste multiple YouTube URLs (one per line)
 */

import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "./ui/alert";

interface UrlInputProps {
  onSubmit: (urls: string[]) => void;
  isLoading?: boolean;
}

/**
 * Validates if a URL is a valid YouTube URL
 */
function isValidYouTubeUrl(url: string): boolean {
  const patterns = [
    /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
    /^https?:\/\/youtu\.be\/[\w-]+/,
    /^https?:\/\/m\.youtube\.com\/watch\?v=[\w-]+/,
  ];
  return patterns.some((pattern) => pattern.test(url));
}

/**
 * Parses textarea input into array of valid YouTube URLs
 */
function parseUrls(input: string): { valid: string[]; invalid: string[] } {
  const lines = input
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  const valid: string[] = [];
  const invalid: string[] = [];

  for (const line of lines) {
    if (isValidYouTubeUrl(line)) {
      valid.push(line);
    } else {
      invalid.push(line);
    }
  }

  return { valid, invalid };
}

export function UrlInput({ onSubmit, isLoading = false }: UrlInputProps) {
  const [input, setInput] = useState("");
  const [validationError, setValidationError] = useState<string>("");
  const [urlCount, setUrlCount] = useState(0);

  // Count URLs as user types
  const handleInputChange = (value: string) => {
    setInput(value);
    const lines = value.split("\n").filter(line => line.trim().length > 0);
    setUrlCount(lines.length);
  };

  const handleSubmit = () => {
    setValidationError("");

    if (!input.trim()) {
      setValidationError("Please paste at least one YouTube URL");
      return;
    }

    const { valid, invalid } = parseUrls(input);

    if (valid.length === 0) {
      setValidationError(
        "No valid YouTube URLs found. Please check the format."
      );
      return;
    }

    if (invalid.length > 0) {
      setValidationError(
        `Warning: ${invalid.length} invalid URL(s) will be skipped. Proceeding with ${valid.length} valid URL(s).`
      );
    }

    onSubmit(valid);
  };

  const handleClear = () => {
    setInput("");
    setValidationError("");
    setUrlCount(0);
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center justify-between mb-2">
          <label htmlFor="url-input" className="block text-sm font-medium">
            YouTube Video URLs
          </label>
          {urlCount > 0 && (
            <span className="text-xs text-muted-foreground">
              {urlCount} URL{urlCount !== 1 ? 's' : ''} entered
            </span>
          )}
        </div>
        <Textarea
          id="url-input"
          value={input}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={`Paste YouTube video URLs here (one per line):\n\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ\nhttps://youtu.be/jNQXAC9IVRw\nhttps://www.youtube.com/watch?v=9bZkp7q19f0`}
          rows={10}
          className="font-mono text-sm resize-y"
          disabled={isLoading}
        />
        <p className="text-xs text-muted-foreground mt-2">
          Supported formats: youtube.com/watch?v=ID, youtu.be/ID, m.youtube.com/watch?v=ID
        </p>
      </div>

      {validationError && (
        <Alert
          variant={
            validationError.startsWith("Warning") ? "default" : "destructive"
          }
        >
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{validationError}</AlertDescription>
        </Alert>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <Button 
          onClick={handleSubmit} 
          disabled={isLoading || !input.trim()}
          className="sm:flex-1"
          size="lg"
        >
          {isLoading ? (
            <>
              <AlertCircle className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            "Download All Videos"
          )}
        </Button>
        <Button
          variant="outline"
          onClick={handleClear}
          disabled={isLoading || !input.trim()}
          size="lg"
        >
          Clear
        </Button>
      </div>
    </div>
  );
}

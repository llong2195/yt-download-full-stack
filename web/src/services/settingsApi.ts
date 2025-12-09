/**
 * Settings API client
 */

import { fetchApi } from "./api";
import type {
  GlobalSettings,
  GlobalSettingsUpdateRequest,
} from "@/types/settings";

export async function fetchSettings(): Promise<GlobalSettings> {
  return fetchApi<GlobalSettings>("/settings");
}

export async function updateSettings(
  request: GlobalSettingsUpdateRequest
): Promise<GlobalSettings> {
  return fetchApi<GlobalSettings>("/settings", {
    method: "PUT",
    body: JSON.stringify(request),
  });
}

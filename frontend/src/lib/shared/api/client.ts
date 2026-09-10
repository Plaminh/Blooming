import { env } from "$env/dynamic/public";
import type { JsonValue } from "$lib/shared/types";
import { joinUrl } from "$lib/shared/utils";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export class ApiError extends Error {
  readonly status: number;
  readonly statusText: string;
  readonly body: string | null;

  constructor(status: number, statusText: string, body: string | null) {
    super(`API request failed with ${status} ${statusText}`);
    this.name = "ApiError";
    this.status = status;
    this.statusText = statusText;
    this.body = body;
  }
}

export type JsonRequestOptions = Omit<RequestInit, "body"> & {
  body?: JsonValue;
};

export function getApiBaseUrl(): string {
  const configured = env.PUBLIC_API_BASE_URL?.trim();
  return configured && configured.length > 0
    ? configured.replace(/\/+$/, "")
    : DEFAULT_API_BASE_URL;
}

export async function apiRequest<T>(
  path: string,
  options: JsonRequestOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  if (options.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(joinUrl(getApiBaseUrl(), path), {
    ...options,
    headers,
    body:
      options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  const text = await response.text();

  if (!response.ok) {
    throw new ApiError(
      response.status,
      response.statusText,
      text.length > 0 ? text : null,
    );
  }

  if (text.length === 0) {
    return undefined as T;
  }

  return JSON.parse(text) as T;
}

export const apiClient = {
  get<T>(path: string, init?: JsonRequestOptions): Promise<T> {
    return apiRequest<T>(path, { ...init, method: "GET" });
  },
  post<T>(
    path: string,
    body?: JsonValue,
    init?: JsonRequestOptions,
  ): Promise<T> {
    return apiRequest<T>(path, { ...init, method: "POST", body });
  },
};

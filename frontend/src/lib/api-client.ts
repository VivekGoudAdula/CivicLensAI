import { env } from "@/config/env";

export interface ApiErrorBody {
  success: false;
  error: {
    message: string;
    status_code: number;
    details?: unknown;
  };
}

export class ApiError extends Error {
  readonly statusCode: number;
  readonly details?: unknown;

  constructor(message: string, statusCode: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.details = details;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

function buildUrl(path: string, params?: RequestOptions["params"]): string {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${base}${normalizedPath}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    });
  }

  return url.toString();
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type");
  const isJson = contentType?.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    if (isJson && typeof payload === "object" && payload !== null && "error" in payload) {
      const errorBody = payload as ApiErrorBody;
      throw new ApiError(
        errorBody.error.message,
        errorBody.error.status_code,
        errorBody.error.details,
      );
    }

    throw new ApiError(
      typeof payload === "string" ? payload : "Request failed",
      response.status,
    );
  }

  return payload as T;
}

export async function apiClient<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, params, headers, ...rest } = options;

  const token = localStorage.getItem("civiclens_token");
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(buildUrl(path, params), {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...authHeader,
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  return parseResponse<T>(response);
}

export interface ServiceStatus {
  name: string;
  status: string;
  message?: string | null;
}

export interface HealthResponse {
  success: boolean;
  status: string;
  app_name: string;
  version: string;
  environment: string;
  services: ServiceStatus[];
}

export const healthApi = {
  check: () => apiClient<HealthResponse>("/health"),
};

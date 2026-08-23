import { appConfig } from "@/lib/config";
import type { ApiErrorResponse } from "@/lib/auth-types";

export class ApiError extends Error {
  status: number;
  code?: string;
  requestId?: string;
  details?: Record<string, unknown>;

  constructor(
    message: string,
    status: number,
    options?: {
      code?: string;
      requestId?: string;
      details?: Record<string, unknown>;
    },
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = options?.code;
    this.requestId = options?.requestId;
    this.details = options?.details;
  }
}

type ApiRequestOptions = RequestInit & {
  token?: string;
};

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { token, headers, ...requestOptions } = options;

  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...requestOptions,
    headers: {
      "Content-Type": "application/json",
      ...headers,
      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),
    },
  });

  if (!response.ok) {
    let message = `API request failed with status ${response.status}`;
    let code: string | undefined;
    let requestId: string | undefined;
    let details: Record<string, unknown> | undefined;

    try {
      const body = (await response.json()) as ApiErrorResponse;

      if (body.error) {
        message = body.error.message;
        code = body.error.code;
        requestId = body.error.request_id;
        details = body.error.details;
      }
    } catch {
      // Keep the fallback message for non-JSON responses.
    }

    throw new ApiError(message, response.status, {
      code,
      requestId,
      details,
    });
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
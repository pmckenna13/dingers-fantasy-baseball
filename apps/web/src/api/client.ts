/**
 * Thin fetch wrapper around the FastAPI backend.
 *
 * Keeps the access token in memory only (never localStorage — an XSS'd page
 * shouldn't be able to read it off disk), and always sends credentials so
 * the httpOnly refresh cookie rides along on same-site requests. Access
 * tokens are short-lived by design (see docs/adr/0001-jwt-over-sessions.md),
 * so on a 401 we transparently try /auth/refresh once before failing.
 */

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
  ) {
    super(`API error ${status}`);
  }
}

async function request<T>(path: string, options: RequestInit = {}, retried = false): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401 && !retried && path !== "/api/v1/auth/refresh") {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return request<T>(path, options, true);
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

async function tryRefresh(): Promise<boolean> {
  try {
    const data = await request<{ access_token: string }>("/api/v1/auth/refresh", {
      method: "POST",
    });
    setAccessToken(data.access_token);
    return true;
  } catch {
    setAccessToken(null);
    return false;
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
};

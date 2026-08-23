import type { LoginResponse, UserSummary } from "@/lib/auth-types";

const ACCESS_TOKEN_KEY = "platform-launchpad-access-token";
const USER_KEY = "platform-launchpad-user";

export function saveSession(response: LoginResponse): void {
  sessionStorage.setItem(
    ACCESS_TOKEN_KEY,
    response.access_token,
  );

  sessionStorage.setItem(
    USER_KEY,
    JSON.stringify(response.user),
  );
}

export function clearSession(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getCurrentUser(): UserSummary | null {
  const value = sessionStorage.getItem(USER_KEY);

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as UserSummary;
  } catch {
    clearSession();
    return null;
  }
}
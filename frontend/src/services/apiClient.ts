import {
  getAccessToken,
  removeAccessToken,
  setAccessToken,
} from "@/lib/auth";

import { refreshAccessToken } from "@/services/authApi";


export async function authenticatedFetch(
  url: string,
  options: RequestInit = {},
  tokenOverride?: string,
): Promise<Response> {

  const token =
    tokenOverride ?? getAccessToken();

  if (!token) {
    throw new Error(
      "Your session has expired. Please log in again.",
    );
  }

  const headers = new Headers(
    options.headers,
  );

  headers.set(
    "Authorization",
    `Bearer ${token}`,
  );

  let response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status !== 401) {
    return response;
  }

  try {
    const refreshedToken =
      await refreshAccessToken();

    setAccessToken(refreshedToken);

    const retryHeaders = new Headers(
      options.headers,
    );

    retryHeaders.set(
      "Authorization",
      `Bearer ${refreshedToken}`,
    );

    response = await fetch(url, {
      ...options,
      headers: retryHeaders,
    });

    if (response.status === 401) {
      removeAccessToken();
    }

    return response;

  } catch {
    removeAccessToken();

    throw new Error(
      "Your session has expired. Please log in again.",
    );
  }
}
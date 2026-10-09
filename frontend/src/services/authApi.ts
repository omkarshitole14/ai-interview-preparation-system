const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error(
    "NEXT_PUBLIC_API_URL is not configured.",
  );
}


export type UserResponse = {
  id: number;
  email: string;
  is_active: boolean;
};


export type TokenResponse = {
  access_token: string;
  token_type: string;
};


export type RegisterRequest = {
  email: string;
  password: string;
};


export type LoginRequest = {
  email: string;
  password: string;
};


async function parseResponse(
  response: Response,
) {
  const data =
    await response.json().catch(
      () => null,
    );

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        `Request failed with status ${response.status}.`,
    );
  }

  return data;
}


export async function registerUser(
  request: RegisterRequest,
): Promise<UserResponse> {

  const response = await fetch(
    `${API_URL}/api/auth/register`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(request),
    },
  );

  return parseResponse(
    response,
  ) as Promise<UserResponse>;
}


export async function loginUser(
  request: LoginRequest,
): Promise<TokenResponse> {

  const response = await fetch(
    `${API_URL}/api/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      credentials: "include",
      body: JSON.stringify(request),
    },
  );

  return parseResponse(
    response,
  ) as Promise<TokenResponse>;
}


export async function refreshAccessToken(): Promise<string> {

  const response = await fetch(
    `${API_URL}/api/auth/refresh`,
    {
      method: "POST",
      credentials: "include",
    },
  );

  const data =
    await parseResponse(response);

  return data.access_token;
}


export async function logoutUser(): Promise<void> {

  await fetch(
    `${API_URL}/api/auth/logout`,
    {
      method: "POST",
      credentials: "include",
    },
  ).catch(() => {
    // Local logout must still happen even if
    // the backend is temporarily unavailable.
  });
}


export async function getCurrentUser(
  token: string,
): Promise<UserResponse> {

  const response = await fetch(
    `${API_URL}/api/auth/me`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(
    response,
  ) as Promise<UserResponse>;
}
import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { api, setAccessToken } from "../../api/client";
import { AuthContext } from "./auth-context";
import type { AuthContextValue } from "./auth-context";
import type { User } from "./types";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthContextValue["status"]>("loading");

  const loadCurrentUser = useCallback(async () => {
    try {
      // On page load there's no in-memory access token yet; the request
      // interceptor's 401 -> /auth/refresh flow uses the httpOnly cookie to
      // silently re-establish the session if one is still valid.
      const me = await api.get<User>("/api/v1/auth/me");
      setUser(me);
      setStatus("authenticated");
    } catch {
      setUser(null);
      setStatus("anonymous");
    }
  }, []);

  useEffect(() => {
    void loadCurrentUser();
  }, [loadCurrentUser]);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.post<{ access_token: string }>("/api/v1/auth/login", {
      email,
      password,
    });
    setAccessToken(access_token);
    const me = await api.get<User>("/api/v1/auth/me");
    setUser(me);
    setStatus("authenticated");
  }, []);

  const register = useCallback(
    async (email: string, displayName: string, password: string) => {
      await api.post("/api/v1/auth/register", {
        email,
        display_name: displayName,
        password,
      });
      await login(email, password);
    },
    [login],
  );

  const logout = useCallback(async () => {
    await api.post("/api/v1/auth/logout").catch(() => undefined);
    setAccessToken(null);
    setUser(null);
    setStatus("anonymous");
  }, []);

  return (
    <AuthContext.Provider value={{ user, status, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

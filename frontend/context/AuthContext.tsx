"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { User, Workspace } from "@/types";
import { api } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  workspace: Workspace | null;
  workspaces: Workspace[];
  token: string | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  switchWorkspace: (workspaceId: string) => Promise<void>;
  refreshWorkspace: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const initAuth = async (savedToken: string) => {
    try {
      setToken(savedToken);
      const me = await api.auth.getMe();
      setUser(me);

      const wsList = await api.workspaces.list();
      setWorkspaces(wsList);

      const savedWsId = localStorage.getItem("workspace_id");
      let activeWs = wsList.find((w: Workspace) => w.id === savedWsId);
      if (!activeWs && wsList.length > 0) {
        activeWs = wsList[0];
        localStorage.setItem("workspace_id", activeWs.id);
      }
      setWorkspace(activeWs || null);
    } catch (err) {
      console.error("Auth init error:", err);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken && savedToken !== "undefined" && savedToken !== "null" && savedToken.trim() !== "") {
      initAuth(savedToken);
    } else {
      localStorage.removeItem("token");
      setIsLoading(false);
    }
  }, []);

  const login = async (newToken: string) => {
    localStorage.setItem("token", newToken);
    await initAuth(newToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("workspace_id");
    setToken(null);
    setUser(null);
    setWorkspace(null);
    setWorkspaces([]);
    setIsLoading(false);
  };

  const switchWorkspace = async (workspaceId: string) => {
    localStorage.setItem("workspace_id", workspaceId);
    const target = workspaces.find((w) => w.id === workspaceId);
    if (target) {
      setWorkspace(target);
    }
  };

  const refreshWorkspace = async () => {
    try {
      const current = await api.workspaces.getCurrent();
      setWorkspace(current);
      const wsList = await api.workspaces.list();
      setWorkspaces(wsList);
    } catch (err) {
      console.error("Failed to refresh workspace:", err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        workspace,
        workspaces,
        token,
        isLoading,
        login,
        logout,
        switchWorkspace,
        refreshWorkspace,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

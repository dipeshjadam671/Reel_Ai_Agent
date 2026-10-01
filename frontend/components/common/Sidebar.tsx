"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Layers,
  CheckCircle2,
  Share2,
  BarChart3,
  Settings,
  Sparkles,
  DollarSign,
  ChevronDown,
  Building2,
  LogOut,
  Video,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Content Tasks", href: "/tasks", icon: Layers },
  { name: "Approvals Queue", href: "/approvals", icon: CheckCircle2, showBadge: true },
  { name: "Social Channels", href: "/social-accounts", icon: Share2 },
  { name: "Analytics & Spend", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { workspace, workspaces, switchWorkspace, logout, user } = useAuth();
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState(0);
  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const fetchPending = async () => {
      try {
        const pending = await api.approvals.listPending();
        if (isMounted) setPendingApprovalsCount(pending.length);
      } catch (err) {
        // quiet fallback
      }
    };
    fetchPending();
    const interval = setInterval(fetchPending, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const spendPercentage = workspace?.monthly_budget_usd
    ? Math.min(100, Math.round(((workspace.current_spend_usd || 0) / workspace.monthly_budget_usd) * 100))
    : 0;

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col h-screen fixed left-0 top-0 z-40 select-none">
      {/* Brand Logo */}
      <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Video className="w-5 h-5 text-slate-950" />
          </div>
          <div>
            <div className="font-bold text-base text-slate-100 flex items-center gap-1.5 leading-none">
              ReelAI <Sparkles className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" />
            </div>
            <div className="text-[10px] text-emerald-400 tracking-wider uppercase font-semibold mt-1">Autonomous Studio</div>
          </div>
        </Link>
      </div>

      {/* Workspace Switcher */}
      <div className="p-3 border-b border-slate-800/60 relative">
        <button
          onClick={() => setIsWorkspaceOpen(!isWorkspaceOpen)}
          className="w-full flex items-center justify-between p-2 rounded-lg bg-slate-900 hover:bg-slate-800/80 border border-slate-800 text-left transition text-sm"
        >
          <div className="flex items-center gap-2 overflow-hidden">
            <Building2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="truncate font-medium text-slate-200">
              {workspace?.name || "Select Workspace"}
            </span>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-400 shrink-0" />
        </button>

        {isWorkspaceOpen && (
          <div className="absolute top-full left-3 right-3 mt-1 py-1 bg-slate-900 border border-slate-800 rounded-lg shadow-xl z-50">
            <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Workspaces
            </div>
            {workspaces.map((ws) => (
              <button
                key={ws.id}
                onClick={() => {
                  switchWorkspace(ws.id);
                  setIsWorkspaceOpen(false);
                }}
                className={`w-full px-3 py-2 text-left text-xs flex items-center justify-between hover:bg-slate-800 ${
                  ws.id === workspace?.id ? "text-emerald-400 font-semibold bg-emerald-500/10" : "text-slate-300"
                }`}
              >
                <span className="truncate">{ws.name}</span>
                {ws.id === workspace?.id && <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Active</span>}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? "bg-gradient-to-r from-emerald-500/15 to-teal-500/10 text-emerald-400 border border-emerald-500/30 font-semibold shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/80"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
                <span>{item.name}</span>
              </div>
              {item.showBadge && pendingApprovalsCount > 0 && (
                <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {pendingApprovalsCount}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Spend Meter & User Profile */}
      <div className="p-4 border-t border-slate-800/80 space-y-3 bg-slate-950/80">
        {/* Budget Meter */}
        <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800/70">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              Monthly Spend
            </span>
            <span className="text-slate-300 font-semibold">
              {formatCurrency(workspace?.current_spend_usd || 0)} / {formatCurrency(workspace?.monthly_budget_usd || 50)}
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                spendPercentage > 85 ? "bg-red-500" : spendPercentage > 60 ? "bg-amber-500" : "bg-emerald-500"
              }`}
              style={{ width: `${spendPercentage}%` }}
            />
          </div>
        </div>

        {/* User bar */}
        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="w-7 h-7 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 flex items-center justify-center font-bold text-xs uppercase">
              {user?.full_name ? user.full_name[0] : user?.email ? user.email[0] : "U"}
            </div>
            <div className="truncate text-xs">
              <p className="font-semibold text-slate-200 truncate">{user?.full_name || "Creator"}</p>
              <p className="text-[10px] text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            title="Log out"
            className="p-1.5 rounded-md text-slate-400 hover:text-red-400 hover:bg-slate-900 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

"use client";

import React from "react";
import Link from "next/link";
import { Plus, Zap, RefreshCw } from "lucide-react";

interface HeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function Header({ title, description, actions }: HeaderProps) {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/50 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-30">
      <div>
        <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          {title}
        </h1>
        {description && (
          <p className="text-xs text-slate-400 mt-0.5">{description}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Mock Mode badge */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>Zero-Cost Local Mode</span>
        </div>

        {actions}

        {!actions && (
          <Link
            href="/tasks/new"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>New Video Task</span>
          </Link>
        )}
      </div>
    </header>
  );
}

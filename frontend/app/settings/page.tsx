"use client";

import React, { useState, useEffect } from "react";
import {
  Settings,
  Building2,
  DollarSign,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Cpu,
  Database,
  Lock,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function SettingsPage() {
  const { workspace, refreshWorkspace } = useAuth();
  const [name, setName] = useState("");
  const [monthlyBudget, setMonthlyBudget] = useState(50);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (workspace) {
      setName(workspace.name);
      setMonthlyBudget(workspace.monthly_budget_usd || 50);
    }
  }, [workspace]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workspace) return;
    try {
      setLoading(true);
      setError(null);
      await api.workspaces.update(workspace.id, {
        name,
        monthly_budget_usd: Number(monthlyBudget),
      });
      await refreshWorkspace();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err?.message || "Failed to update workspace settings.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <Header
        title="Workspace Settings"
        description="Manage workspace identity, budget hard-caps, and AI engine parameters."
      />

      <div className="p-8 max-w-4xl space-y-8 flex-1 overflow-y-auto">
        {success && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Workspace settings updated successfully!</span>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{typeof error === "string" ? error : JSON.stringify(error)}</span>
          </div>
        )}

        {/* Form: Workspace Details */}
        <form onSubmit={handleSave} className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <Building2 className="w-4 h-4" />
              <span>Workspace Profile</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Workspace Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Workspace ID (Tenant Key)
                </label>
                <input
                  type="text"
                  readOnly
                  value={workspace?.id || ""}
                  className="w-full bg-slate-950/60 border border-slate-800/60 rounded-xl px-3.5 py-2.5 text-xs text-slate-400 font-mono cursor-not-allowed"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Monthly AI Spend Limit ($USD)
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="number"
                  min="5"
                  max="10000"
                  step="5"
                  value={monthlyBudget}
                  onChange={(e) => setMonthlyBudget(Number(e.target.value))}
                  className="w-40 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
                <span className="text-xs text-slate-400">
                  Current spend:{" "}
                  <strong className="text-emerald-400 font-mono">
                    {formatCurrency(workspace?.current_spend_usd || 0)}
                  </strong>
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                The platform automatically halts all agent generation cycles when this monthly ceiling is reached.
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 transition disabled:opacity-50"
              >
                {loading ? "Saving..." : "Save Workspace Changes"}
              </button>
            </div>
          </div>
        </form>

        {/* System & Engine Architecture Status */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
            <Cpu className="w-4 h-4" />
            <span>AI Architecture & Engine Capabilities</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 block font-medium">Orchestration Graph</span>
              <p className="text-slate-200 font-semibold">LangGraph with Human-in-the-Loop interrupt()</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 block font-medium">Video Rendering Engine</span>
              <p className="text-slate-200 font-semibold">FFmpeg (1080x1920 9:16 Vertical Composition)</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 block font-medium">Audio Normalization</span>
              <p className="text-slate-200 font-semibold">-14 LUFS (EBU R128) + Sidechain Ducking</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-slate-400 block font-medium">Semantic Deduplication</span>
              <p className="text-slate-200 font-semibold">pgvector 1536-dim Cosine Similarity (Novelty Guard)</p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span>Multi-Tenant Data Isolation: Active across all database schemas & storage buckets.</span>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

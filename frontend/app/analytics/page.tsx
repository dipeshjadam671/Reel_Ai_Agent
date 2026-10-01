"use client";

import React, { useEffect, useState } from "react";
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Video,
  Share2,
  Heart,
  RefreshCw,
  Sparkles,
  PieChart,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Analytics } from "@/types";

export default function AnalyticsPage() {
  const { workspace } = useAuth();
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.analytics.getOverview();
      setData(res);
    } catch (err) {
      console.error("Failed to load analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [workspace?.id]);

  const spendPct = data?.monthly_budget_usd
    ? Math.min(100, Math.round(((data.total_spend_usd || 0) / data.monthly_budget_usd) * 100))
    : 0;

  return (
    <DashboardLayout>
      <Header
        title="Analytics & Spend Ledger"
        description="Monitor multi-tenant infrastructure cost ledger and social performance."
        actions={
          <button
            onClick={fetchAnalytics}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
            title="Refresh metrics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        }
      />

      <div className="p-8 space-y-6 flex-1 overflow-y-auto">
        {/* Top KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Videos Produced</span>
              <Video className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">
              {data?.total_videos_created || 0}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              Published: {data?.total_videos_published || 0}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Total Views</span>
              <TrendingUp className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">
              {(data?.total_views || 0).toLocaleString()}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">Across all linked channels</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Total Engagements</span>
              <Heart className="w-4 h-4 text-pink-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">
              {((data?.total_likes || 0) + (data?.total_shares || 0)).toLocaleString()}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              {data?.total_likes || 0} likes • {data?.total_shares || 0} shares
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Current Spend</span>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">
              {formatCurrency(data?.total_spend_usd || 0)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              Budget: {formatCurrency(data?.monthly_budget_usd || 50)} ({spendPct}%)
            </div>
          </div>
        </div>

        {/* Spend Progress Bar */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200">Monthly Workspace Budget Utilization</span>
            <span className="font-mono text-slate-400">
              {formatCurrency(data?.total_spend_usd || 0)} of {formatCurrency(data?.monthly_budget_usd || 50)} limit
            </span>
          </div>

          <div className="w-full bg-slate-950 rounded-full h-3 border border-slate-800 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                spendPct > 85 ? "bg-red-500" : spendPct > 60 ? "bg-amber-500" : "bg-emerald-500"
              }`}
              style={{ width: `${spendPct}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
            <span>Hard-stop triggered automatically at 100% threshold.</span>
            <span>{Math.max(0, 100 - spendPct)}% Remaining</span>
          </div>
        </div>

        {/* Granular Spend Ledger Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-sm font-bold text-slate-100">Granular AI Spend Ledger</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live audit trail of micro-transactions per provider (LLM, TTS, Avatar, Search, Render).
            </p>
          </div>

          {(!data?.recent_spend_records || data.recent_spend_records.length === 0) ? (
            <div className="p-10 text-center text-xs text-slate-500">
              No spend records logged yet. Spend entries are recorded whenever an agent calls a provider.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-5 py-3">Timestamp</th>
                    <th className="px-5 py-3">Provider</th>
                    <th className="px-5 py-3">Operation</th>
                    <th className="px-5 py-3">Cycle ID</th>
                    <th className="px-5 py-3 text-right">Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {data.recent_spend_records.map((rec) => (
                    <tr key={rec.id} className="hover:bg-slate-800/30 transition">
                      <td className="px-5 py-3 text-slate-400">{formatDate(rec.created_at)}</td>
                      <td className="px-5 py-3">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-semibold text-slate-200 capitalize">
                          {rec.provider}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-slate-300">{rec.operation}</td>
                      <td className="px-5 py-3 font-mono text-[11px] text-slate-400">
                        {rec.cycle_id ? `${rec.cycle_id.slice(0, 8)}...` : "-"}
                      </td>
                      <td className="px-5 py-3 text-right font-mono text-emerald-400 font-semibold">
                        {formatCurrency(rec.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Layers,
  Video,
  CheckCircle2,
  TrendingUp,
  DollarSign,
  Play,
  ArrowRight,
  Sparkles,
  Clock,
  ExternalLink,
  RefreshCw,
  Loader2,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Task, Cycle } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const { workspace } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [cycles, setCycles] = useState<Cycle[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [runningTaskId, setRunningTaskId] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [tList, cList, aData] = await Promise.all([
        api.tasks.list(0, 10),
        api.cycles.list({ limit: 10 }),
        api.analytics.getOverview().catch(() => null),
      ]);
      setTasks(tList);
      setCycles(cList);
      setAnalytics(aData);
    } catch (err) {
      console.error("Dashboard data load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [workspace?.id]);

  const handleRunTask = async (taskId: string) => {
    if (runningTaskId) return;
    try {
      setRunningTaskId(taskId);
      const res = await api.tasks.runNow(taskId);
      const cycleId = res?.id || (res as any)?.cycle_id;
      if (cycleId) {
        router.push(`/cycles/${cycleId}`);
      } else {
        await fetchData();
      }
    } catch (err: any) {
      alert(err?.message || "Failed to trigger cycle");
      await fetchData();
    } finally {
      setRunningTaskId(null);
    }
  };

  const pendingCycles = cycles.filter((c) => c.status === "pending_approval");

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending_approval":
        return (
          <span className="px-2.5 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[11px] font-semibold flex items-center gap-1 w-max">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            Needs Approval
          </span>
        );
      case "completed":
        return (
          <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[11px] font-semibold flex items-center gap-1 w-max">
            <CheckCircle2 className="w-3 h-3" />
            Published
          </span>
        );
      case "failed":
        return (
          <span className="px-2.5 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-400 text-[11px] font-semibold w-max">
            Failed
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[11px] font-semibold flex items-center gap-1 w-max">
            <Sparkles className="w-3 h-3 animate-spin" />
            {status.replace(/_/g, " ")}
          </span>
        );
    }
  };

  return (
    <DashboardLayout>
      <Header
        title="Dashboard Overview"
        description="Autonomous AI video generation activity, pipelines, and performance."
        actions={
          <button
            onClick={fetchData}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
            title="Refresh dashboard"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        }
      />

      <div className="p-8 space-y-8 flex-1 overflow-y-auto">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Active Tasks */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-lg">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Configured Tasks</span>
              <Layers className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">{tasks.length}</div>
            <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
              <span>Automated topic listeners</span>
            </div>
          </div>

          {/* Pending Approvals */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-lg relative overflow-hidden">
            {pendingCycles.length > 0 && (
              <div className="absolute top-0 right-0 w-16 h-16 bg-amber-500/10 rounded-bl-full pointer-events-none" />
            )}
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Approval Queue</span>
              <CheckCircle2 className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-300">{pendingCycles.length}</div>
            <Link
              href="/approvals"
              className="text-[11px] text-amber-400/90 hover:text-amber-300 font-semibold mt-1 flex items-center gap-1 transition"
            >
              <span>Review pending videos</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {/* Total Views */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-lg">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Total Social Views</span>
              <TrendingUp className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">
              {(analytics?.total_views || 0).toLocaleString()}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">Across YT, IG & TikTok</div>
          </div>

          {/* Spend vs Budget */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-lg">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Monthly AI Spend</span>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">
              {formatCurrency(workspace?.current_spend_usd || 0)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              Budget: {formatCurrency(workspace?.monthly_budget_usd || 50)}
            </div>
          </div>
        </div>

        {/* Quick Launch Section */}
        {tasks.length > 0 && (
          <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-teal-950/20 border border-emerald-900/30 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  Instant Pipeline Run
                </h3>
                <p className="text-xs text-slate-400">
                  Trigger an autonomous end-to-end video cycle immediately on one of your configured tasks.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {tasks.slice(0, 3).map((task) => {
                const isRunning =
                  runningTaskId === task.id ||
                  ["created", "researching", "scripting", "producing"].includes(task.latest_cycle_status || "");
                const isPendingApproval = task.latest_cycle_status === "pending_approval";
                const isPublished = task.latest_cycle_status === "published";

                return (
                  <div
                    key={task.id}
                    className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-3"
                  >
                    <div className="truncate">
                      <p className="text-xs font-semibold text-slate-200 truncate">{task.name}</p>
                      <p className="text-[11px] text-slate-400 truncate">{task.topic}</p>
                    </div>
                    {isPendingApproval ? (
                      <Link
                        href="/approvals"
                        className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold flex items-center gap-1.5 shrink-0 transition"
                      >
                        <CheckCircle2 className="w-3 h-3 text-amber-400" />
                        <span>Review</span>
                      </Link>
                    ) : isPublished ? (
                      <Link
                        href={`/cycles/${task.latest_cycle_id}`}
                        className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-400 text-xs font-semibold flex items-center gap-1.5 shrink-0 transition"
                      >
                        <CheckCircle2 className="w-3 h-3" />
                        <span>View</span>
                      </Link>
                    ) : isRunning ? (
                      <button
                        disabled
                        className="px-3 py-1.5 rounded-lg bg-emerald-600/40 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shrink-0 cursor-not-allowed border border-emerald-500/30"
                      >
                        <Loader2 className="w-3 h-3 animate-spin" />
                        <span>Running...</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => handleRunTask(task.id)}
                        disabled={Boolean(runningTaskId)}
                        className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold flex items-center gap-1.5 shrink-0 shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
                      >
                        <Play className="w-3 h-3 fill-white" />
                        <span>Run</span>
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Recent Cycles Table */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-100">Recent Video Cycles</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time execution status of the multi-agent production pipelines.
              </p>
            </div>
            <Link
              href="/tasks"
              className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1 transition"
            >
              <span>Manage Tasks</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {cycles.length === 0 ? (
            <div className="p-12 text-center">
              <Video className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-300">No content cycles yet</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Trigger a run from your configured tasks above, or create a new task to start producing vertical videos.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-5 py-3">Cycle ID</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3">Novelty</th>
                    <th className="px-5 py-3">Cost</th>
                    <th className="px-5 py-3">Created</th>
                    <th className="px-5 py-3 text-right">Pipeline</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {cycles.map((cycle) => (
                    <tr key={cycle.id} className="hover:bg-slate-800/30 transition">
                      <td className="px-5 py-4 font-mono text-[11px] text-slate-400">
                        {cycle.id.slice(0, 8)}...
                      </td>
                      <td className="px-5 py-4">{getStatusBadge(cycle.status)}</td>
                      <td className="px-5 py-4">
                        {cycle.novelty_score !== null && cycle.novelty_score !== undefined ? (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              cycle.novelty_score > 0.8
                                ? "bg-emerald-500/20 text-emerald-300"
                                : cycle.novelty_score > 0.5
                                ? "bg-amber-500/20 text-amber-300"
                                : "bg-red-500/20 text-red-300"
                            }`}
                          >
                            {(cycle.novelty_score * 100).toFixed(0)}% Original
                          </span>
                        ) : (
                          <span className="text-slate-500">-</span>
                        )}
                      </td>
                      <td className="px-5 py-4 font-mono text-slate-300">
                        {formatCurrency(cycle.actual_cost_usd || cycle.estimated_cost_usd || 0)}
                      </td>
                      <td className="px-5 py-4 text-slate-400">
                        {formatDate(cycle.created_at)}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <Link
                          href={`/cycles/${cycle.id}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold transition"
                        >
                          <span>Inspect</span>
                          <ExternalLink className="w-3 h-3" />
                        </Link>
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

"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Play,
  Layers,
  Sparkles,
  Calendar,
  Globe2,
  Trash2,
  ExternalLink,
  CheckCircle2,
  Loader2,
  Clock,
  Edit3,
  X,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { api } from "@/lib/api";
import { formatDate, formatCurrency } from "@/lib/utils";
import { Task, Cycle } from "@/types";
import { getAvatarById } from "@/lib/avatars";

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [cycles, setCycles] = useState<Cycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  // Edit Schedule Modal State
  const [isEditScheduleOpen, setIsEditScheduleOpen] = useState(false);
  const [editFreq, setEditFreq] = useState("daily");
  const [editTime, setEditTime] = useState("09:00");
  const [editTz, setEditTz] = useState("UTC");
  const [savingSchedule, setSavingSchedule] = useState(false);

  const fetchTaskAndCycles = async () => {
    try {
      setLoading(true);
      const [tData, cData] = await Promise.all([
        api.tasks.get(taskId),
        api.cycles.list({ task_id: taskId }),
      ]);
      setTask(tData);
      setCycles(cData);
    } catch (err) {
      console.error("Failed to load task:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (taskId) fetchTaskAndCycles();
  }, [taskId]);

  const handleRunTask = async () => {
    if (running) return;
    try {
      setRunning(true);
      const res = await api.tasks.runNow(taskId);
      const cycleId = res?.id || (res as any)?.cycle_id;
      if (cycleId) {
        router.push(`/cycles/${cycleId}`);
      } else {
        await fetchTaskAndCycles();
      }
    } catch (err: any) {
      alert(err?.message || "Failed to trigger cycle");
      await fetchTaskAndCycles();
    } finally {
      setRunning(false);
    }
  };

  const openEditSchedule = () => {
    setEditFreq(task?.schedule_config?.frequency || "daily");
    setEditTime(task?.schedule_config?.time || "09:00");
    setEditTz(task?.schedule_config?.timezone || "UTC");
    setIsEditScheduleOpen(true);
  };

  const handleSaveSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSavingSchedule(true);
      await api.tasks.update(taskId, {
        schedule_config: {
          frequency: editFreq,
          time: editTime,
          timezone: editTz,
          active_days: task?.schedule_config?.active_days || ["mon", "tue", "wed", "thu", "fri"],
        },
      });
      setIsEditScheduleOpen(false);
      await fetchTaskAndCycles();
    } catch (err: any) {
      alert(err?.message || "Failed to update schedule");
    } finally {
      setSavingSchedule(false);
    }
  };

  const isRunning =
    running ||
    ["created", "researching", "scripting", "producing"].includes(task?.latest_cycle_status || "");
  const isPendingApproval = task?.latest_cycle_status === "pending_approval";
  const isPublished = task?.latest_cycle_status === "published";

  if (!task && !loading) {
    return (
      <DashboardLayout>
        <div className="p-12 text-center text-slate-400">Task not found</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Header
        title={task?.name || "Task Configuration"}
        description={`ID: ${taskId}`}
        actions={
          <div className="flex items-center gap-2">
            <Link
              href="/tasks"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300 hover:bg-slate-900 text-xs font-semibold transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </Link>

            {isPendingApproval ? (
              <Link
                href="/approvals"
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold shadow-sm transition"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                <span>Review Video in Approvals</span>
              </Link>
            ) : isPublished ? (
              <Link
                href={`/cycles/${task?.latest_cycle_id}`}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-400 text-xs font-semibold transition"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>View Video</span>
              </Link>
            ) : isRunning ? (
              <button
                disabled
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600/40 text-emerald-300 text-xs font-semibold cursor-not-allowed border border-emerald-500/30"
              >
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Generating Video...</span>
              </button>
            ) : (
              <button
                onClick={handleRunTask}
                disabled={running}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Trigger Cycle Now</span>
              </button>
            )}
          </div>
        }
      />

      <div className="p-8 space-y-6 flex-1 overflow-y-auto">
        {/* Task Config Overview Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="md:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div>
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                Topic & Content Angle
              </span>
              <p className="text-sm font-semibold text-slate-100 mt-1">{task?.topic}</p>
            </div>

            {task?.seed_script && (
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Seed Script / Prompt
                </span>
                <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800/80 mt-1 whitespace-pre-wrap">
                  {task.seed_script}
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-3 border-t border-slate-800 text-xs">
              <div>
                <span className="text-slate-500 block">Language</span>
                <span className="font-semibold text-slate-200 uppercase">{task?.language}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Presenter Layout</span>
                <span className="font-semibold text-slate-200 capitalize">
                  {task?.presenter_config?.layout || "PIP"}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">Target Platforms</span>
                <div className="flex gap-1 mt-0.5">
                  {task?.target_platforms.map((p) => (
                    <span key={p} className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300 capitalize">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Presenter Persona Showcase */}
            {(() => {
              const persona = getAvatarById(task?.presenter_config?.avatar_id);
              const isMale = persona.gender === "male";
              return (
                <div className="pt-3 border-t border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Studio Video Presenter
                  </span>
                  <div className="flex items-center gap-3.5 p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                    <img
                      src={persona.thumbnail}
                      alt={persona.name}
                      className="w-12 h-12 rounded-xl object-cover ring-2 ring-slate-700/50 shadow-md flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-slate-100">{persona.name}</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                            isMale
                              ? "bg-blue-500/10 text-blue-400 border-blue-500/30"
                              : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                          }`}
                        >
                          {persona.gender}
                        </span>
                        <span className="text-[11px] text-slate-400 bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700/40">
                          {task?.presenter_config?.layout || "PIP"} Layout
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 truncate mt-0.5">
                        {persona.title} • {persona.badge}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>

          {/* Schedule & Metadata */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Autonomous Cadence
              </h3>
              <button
                onClick={openEditSchedule}
                className="px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold flex items-center gap-1.5 transition"
              >
                <Clock className="w-3.5 h-3.5" />
                <span>Edit Schedule</span>
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-slate-400">Frequency</span>
                <span className="font-semibold text-slate-200 capitalize">
                  {task?.schedule_config?.frequency || "Daily"}
                </span>
              </div>
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-slate-400">Run Time</span>
                <span className="font-semibold text-slate-200">
                  {task?.schedule_config?.time || "09:00"} {task?.schedule_config?.timezone || "UTC"}
                </span>
              </div>
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-slate-400">Brand CTA</span>
                <span className="font-semibold text-slate-200 text-right truncate max-w-[140px]">
                  {task?.brand_preferences?.call_to_action || "Follow for more!"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Created</span>
                <span className="text-slate-400">{formatDate(task?.created_at || "")}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Task Cycles History */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-sm font-bold text-slate-100">Execution History</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              All video generation cycles launched under this content task.
            </p>
          </div>

          {cycles.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No cycles have run for this task yet. Click &ldquo;Trigger Cycle Now&rdquo; to launch the autonomous agent team.
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
                    <th className="px-5 py-3">Date</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {cycles.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-800/30 transition">
                      <td className="px-5 py-3 font-mono text-[11px] text-slate-400">
                        {c.id.slice(0, 8)}...
                      </td>
                      <td className="px-5 py-3 font-medium capitalize">
                        {c.status.replace(/_/g, " ")}
                      </td>
                      <td className="px-5 py-3">
                        {c.novelty_score ? `${(c.novelty_score * 100).toFixed(0)}%` : "-"}
                      </td>
                      <td className="px-5 py-3 font-mono">
                        {formatCurrency(c.actual_cost_usd || c.estimated_cost_usd || 0)}
                      </td>
                      <td className="px-5 py-3 text-slate-400">{formatDate(c.created_at)}</td>
                      <td className="px-5 py-3 text-right">
                        <Link
                          href={`/cycles/${c.id}`}
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

      {/* Edit Schedule Modal */}
      {isEditScheduleOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-bold text-slate-100">Edit Post Share Schedule</h3>
              </div>
              <button
                onClick={() => setIsEditScheduleOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveSchedule} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Posting Frequency</label>
                <select
                  value={editFreq}
                  onChange={(e) => setEditFreq(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="daily">Daily (Every Day)</option>
                  <option value="weekdays">Weekdays (Monday – Friday)</option>
                  <option value="weekends">Weekends (Saturday – Sunday)</option>
                  <option value="custom">Custom Active Days</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Post Share Time</label>
                <input
                  type="time"
                  value={editTime}
                  onChange={(e) => setEditTime(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">
                  Select the exact time of day when video generation & publishing should occur.
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Timezone</label>
                <select
                  value={editTz}
                  onChange={(e) => setEditTz(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="UTC">UTC (Coordinated Universal Time)</option>
                  <option value="Asia/Kolkata">Asia/Kolkata (IST +5:30)</option>
                  <option value="America/New_York">America/New_York (EST / EDT)</option>
                  <option value="America/Los_Angeles">America/Los_Angeles (PST / PDT)</option>
                  <option value="America/Chicago">America/Chicago (CST / CDT)</option>
                  <option value="Europe/London">Europe/London (GMT / BST)</option>
                  <option value="Europe/Paris">Europe/Paris (CET / CEST)</option>
                  <option value="Asia/Dubai">Asia/Dubai (GST +4:00)</option>
                  <option value="Asia/Singapore">Asia/Singapore (SGT +8:00)</option>
                  <option value="Asia/Tokyo">Asia/Tokyo (JST +9:00)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsEditScheduleOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingSchedule}
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 transition flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Clock className="w-3.5 h-3.5" />
                  <span>{savingSchedule ? "Saving..." : "Save Schedule"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

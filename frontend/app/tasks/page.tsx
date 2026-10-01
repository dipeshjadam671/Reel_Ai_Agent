"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Layers,
  Plus,
  Play,
  Globe2,
  Calendar,
  Sparkles,
  Trash2,
  Share2,
  Clock,
  ExternalLink,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { formatDate } from "@/lib/utils";
import { Task } from "@/types";
import { getAvatarById } from "@/lib/avatars";

export default function TasksPage() {
  const router = useRouter();
  const { workspace } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningTaskId, setRunningTaskId] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await api.tasks.list();
      setTasks(data);
    } catch (err) {
      console.error("Failed to load tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
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
        await fetchTasks();
      }
    } catch (err: any) {
      alert(err?.message || "Failed to trigger cycle");
      await fetchTasks();
    } finally {
      setRunningTaskId(null);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm("Are you sure you want to delete this content task?")) return;
    try {
      await api.tasks.delete(taskId);
      setTasks(tasks.filter((t) => t.id !== taskId));
    } catch (err: any) {
      alert(err?.message || "Failed to delete task");
    }
  };

  return (
    <DashboardLayout>
      <Header
        title="Content Tasks"
        description="Autonomous generation instructions, target social platforms, and schedules."
        actions={
          <Link
            href="/tasks/new"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>Create Task</span>
          </Link>
        }
      />

      <div className="p-8 space-y-6 flex-1 overflow-y-auto">
        {tasks.length === 0 && !loading ? (
          <div className="p-16 text-center bg-slate-900/60 border border-slate-800 rounded-2xl">
            <Layers className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-200">No Content Tasks Configured</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto mb-5">
              Create your first autonomous video topic, select your language, presenter avatar, and schedule.
            </p>
            <Link
              href="/tasks/new"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition"
            >
              <Plus className="w-4 h-4" />
              <span>Create Task</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {tasks.map((task) => {
              const isRunning =
                runningTaskId === task.id ||
                ["created", "researching", "scripting", "producing"].includes(task.latest_cycle_status || "");
              const isPendingApproval = task.latest_cycle_status === "pending_approval";
              const isPublished = task.latest_cycle_status === "published";

              return (
                <div
                  key={task.id}
                  className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col justify-between hover:border-slate-700/80 transition"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[11px] font-semibold uppercase">
                          {task.language}
                        </span>
                        {isPendingApproval && (
                          <span className="px-2 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-semibold">
                            Video Ready
                          </span>
                        )}
                        {isPublished && (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold">
                            Published
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-800 transition"
                          title="Delete task"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <h3 className="text-base font-bold text-slate-100 mb-1">{task.name}</h3>
                    <p className="text-xs text-slate-400 line-clamp-2 mb-4">{task.topic}</p>

                    <div className="space-y-2 border-t border-slate-800/80 pt-3 text-xs text-slate-400">
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-slate-500">
                          <Share2 className="w-3.5 h-3.5 text-slate-400" />
                          Platforms
                        </span>
                        <div className="flex items-center gap-1">
                          {task.target_platforms.map((p) => (
                            <span
                              key={p}
                              className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] font-medium text-slate-300 capitalize"
                            >
                              {p}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-slate-500">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          Frequency
                        </span>
                        <span className="text-slate-300 font-medium capitalize">
                          {task.schedule_config?.frequency || "Daily"} at {task.schedule_config?.time || "09:00"}
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-slate-500">
                          <Sparkles className="w-3.5 h-3.5 text-slate-400" />
                          Presenter
                        </span>
                        {(() => {
                          const persona = getAvatarById(task.presenter_config?.avatar_id);
                          const isMale = persona.gender === "male";
                          return (
                            <div className="flex items-center gap-1.5">
                              <span className="text-slate-300 font-medium">
                                {persona.name} ({task.presenter_config?.layout || "PIP"})
                              </span>
                              <span
                                className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                                  isMale
                                    ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                                    : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                                }`}
                              >
                                {isMale ? "Male" : "Female"}
                              </span>
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                    <Link
                      href={`/tasks/${task.id}`}
                      className="text-xs text-slate-400 hover:text-slate-200 font-medium flex items-center gap-1 transition"
                    >
                      <span>Config & Cycles</span>
                      <ExternalLink className="w-3 h-3" />
                    </Link>

                    {isPendingApproval ? (
                      <Link
                        href="/approvals"
                        className="px-3.5 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold flex items-center gap-1.5 transition shadow-sm"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                        <span>Review Video</span>
                      </Link>
                    ) : isPublished ? (
                      <Link
                        href={`/cycles/${task.latest_cycle_id}`}
                        className="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-400 text-xs font-semibold flex items-center gap-1.5 transition"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>View Video</span>
                      </Link>
                    ) : isRunning ? (
                      <button
                        disabled
                        className="px-3.5 py-1.5 rounded-xl bg-emerald-600/40 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 cursor-not-allowed border border-emerald-500/30"
                      >
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Generating Video...</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => handleRunTask(task.id)}
                        disabled={Boolean(runningTaskId)}
                        className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
                      >
                        <Play className="w-3 h-3 fill-white" />
                        <span>Run Now</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

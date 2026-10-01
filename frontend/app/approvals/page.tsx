"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  XCircle,
  RotateCcw,
  Sparkles,
  ExternalLink,
  RefreshCw,
  Film,
  Award,
  Video,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { VideoPlayer } from "@/components/video/VideoPlayer";
import { ApprovalModal } from "@/components/approval/ApprovalModal";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Cycle } from "@/types";

export default function ApprovalsPage() {
  const [pendingCycles, setPendingCycles] = useState<Cycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCycleId, setSelectedCycleId] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchPending = async () => {
    try {
      setLoading(true);
      const data = await api.approvals.listPending();
      setPendingCycles(data);
    } catch (err) {
      console.error("Failed to load pending approvals:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const openApprovalModal = (cycleId: string, topic: string) => {
    setSelectedCycleId(cycleId);
    setSelectedTopic(topic);
    setIsModalOpen(true);
  };

  return (
    <DashboardLayout>
      <Header
        title="Human-in-the-Loop Approvals"
        description="Review generated vertical videos before they are published to your social channels."
        actions={
          <button
            onClick={fetchPending}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
            title="Refresh pending approvals"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        }
      />

      <div className="p-8 space-y-6 flex-1 overflow-y-auto">
        {pendingCycles.length === 0 && !loading ? (
          <div className="p-16 text-center bg-slate-900/60 border border-slate-800 rounded-2xl max-w-lg mx-auto">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-200">All Caught Up!</h3>
            <p className="text-xs text-slate-400 mt-1">
              There are no videos waiting for human review. When an autonomous cycle finishes rendering, it will appear here for your sign-off.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pendingCycles.map((c) => (
              <div
                key={c.id}
                className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-2.5 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                      Pending Approval
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {c.id.slice(0, 8)}...
                    </span>
                  </div>

                  {/* Video Player in card */}
                  <div className="w-full flex justify-center mb-4">
                    <VideoPlayer
                      src={api.cycles.getVideoUrl(c.id)}
                      poster={api.cycles.getThumbnailUrl(c.id)}
                      resolution="1080x1920"
                    />
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex items-center justify-between text-slate-400">
                      <span>Novelty Score</span>
                      <span className="font-semibold text-emerald-400">
                        {c.novelty_score ? `${(c.novelty_score * 100).toFixed(0)}%` : "100%"} Original
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-400">
                      <span>Generated</span>
                      <span className="text-slate-300">{formatDate(c.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-slate-800 space-y-2">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openApprovalModal(c.id, "Pending Video Review")}
                      className="flex-1 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-600/25 transition flex items-center justify-center gap-1.5"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Review & Sign Off</span>
                    </button>
                  </div>

                  <Link
                    href={`/cycles/${c.id}`}
                    className="w-full py-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Inspect Pipeline Details</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedCycleId && (
        <ApprovalModal
          cycleId={selectedCycleId}
          topic={selectedTopic}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={() => {
            fetchPending();
          }}
        />
      )}
    </DashboardLayout>
  );
}

"use client";

import React, { useState } from "react";
import { CheckCircle2, XCircle, RotateCcw, AlertCircle, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

interface ApprovalModalProps {
  cycleId: string;
  topic: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function ApprovalModal({
  cycleId,
  topic,
  isOpen,
  onClose,
  onSuccess,
}: ApprovalModalProps) {
  const [feedback, setFeedback] = useState("");
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleApprove = async () => {
    try {
      setLoadingAction("approve");
      setError(null);
      await api.approvals.approve(cycleId);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to approve video.");
    } finally {
      setLoadingAction(null);
    }
  };

  const handleReject = async () => {
    try {
      setLoadingAction("reject");
      setError(null);
      await api.approvals.reject(cycleId, feedback);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to reject cycle.");
    } finally {
      setLoadingAction(null);
    }
  };

  const handleRegenerate = async () => {
    try {
      setLoadingAction("regenerate");
      setError(null);
      await api.approvals.regenerate(cycleId, feedback);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to request regeneration.");
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Human-in-the-Loop Gate</span>
          </div>
          <h2 className="text-lg font-bold text-slate-100">Review & Approve Video</h2>
          <p className="text-xs text-slate-400 mt-1 line-clamp-2">Topic: &ldquo;{topic}&rdquo;</p>
        </div>

        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{typeof error === "string" ? error : JSON.stringify(error)}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Reviewer Notes / Regeneration Feedback (Optional)
            </label>
            <textarea
              rows={3}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="e.g. Make the hook more punchy, or re-verify the statistic in scene 2..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
            />
          </div>

          <div className="text-[11px] text-slate-400 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            Approving will automatically trigger final publishing to all connected platforms configured for this task.
          </div>
        </div>

        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between gap-2">
          <button
            onClick={onClose}
            disabled={!!loadingAction}
            className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 transition"
          >
            Cancel
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={handleReject}
              disabled={!!loadingAction}
              className="px-3.5 py-2 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>{loadingAction === "reject" ? "Rejecting..." : "Reject"}</span>
            </button>

            <button
              onClick={handleRegenerate}
              disabled={!!loadingAction}
              className="px-3.5 py-2 rounded-xl border border-amber-500/30 text-amber-300 hover:bg-amber-500/10 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{loadingAction === "regenerate" ? "Re-running..." : "Regenerate"}</span>
            </button>

            <button
              onClick={handleApprove}
              disabled={!!loadingAction}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-600/25 transition disabled:opacity-50"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{loadingAction === "approve" ? "Publishing..." : "Approve & Publish"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

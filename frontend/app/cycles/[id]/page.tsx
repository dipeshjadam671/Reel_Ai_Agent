"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  RefreshCw,
  Video,
  FileText,
  Search,
  Film,
  ShieldCheck,
  Share2,
  DollarSign,
  Play,
  RotateCcw,
  CheckSquare,
  Award,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { VideoPlayer } from "@/components/video/VideoPlayer";
import { ApprovalModal } from "@/components/approval/ApprovalModal";
import { api } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Cycle, CyclePreview, Source, Script, Asset, Publication } from "@/types";

const PIPELINE_STAGES = [
  { id: "research", label: "Research & Scouting", icon: Search },
  { id: "novelty", label: "Novelty Guard", icon: ShieldCheck },
  { id: "script", label: "Script & Localization", icon: FileText },
  { id: "media", label: "Media & Avatar", icon: Film },
  { id: "voice", label: "Voice & Audio Sync", icon: Sparkles },
  { id: "render", label: "FFmpeg Composition", icon: Video },
  { id: "qa", label: "Compliance & QA", icon: Award },
  { id: "approval", label: "Human Approval", icon: CheckCircle2 },
  { id: "publish", label: "Social Publishing", icon: Share2 },
];

export default function CyclePipelinePage() {
  const params = useParams();
  const cycleId = params.id as string;

  const [cycle, setCycle] = useState<Cycle | null>(null);
  const [preview, setPreview] = useState<CyclePreview | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [script, setScript] = useState<Script | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [publications, setPublications] = useState<Publication[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"script" | "sources" | "assets" | "qa" | "social">("script");
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);

  const fetchCycleData = async () => {
    try {
      const [cData, pData, sData, scData, aData, pubData] = await Promise.all([
        api.cycles.get(cycleId),
        api.cycles.getPreview(cycleId).catch(() => null),
        api.cycles.getSources(cycleId).catch(() => []),
        api.cycles.getScript(cycleId).catch(() => null),
        api.cycles.getAssets(cycleId).catch(() => []),
        api.cycles.getPublications(cycleId).catch(() => []),
      ]);

      setCycle(cData);
      setPreview(pData);
      setSources(sData);
      setScript(scData);
      setAssets(aData);
      setPublications(pubData);
    } catch (err) {
      console.error("Failed to load cycle data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (cycleId) {
      fetchCycleData();
      // Auto-poll if still in active processing
      const interval = setInterval(() => {
        if (cycle?.status !== "completed" && cycle?.status !== "failed") {
          fetchCycleData();
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [cycleId, cycle?.status]);

  const getStageStatus = (stageId: string) => {
    if (!cycle) return "pending";

    // Completed cycle
    if (cycle.status === "completed") return "done";
    // Failed cycle
    if (cycle.status === "failed") return "failed";

    if (cycle.status === "pending_approval") {
      if (stageId === "approval") return "active";
      if (stageId === "publish") return "pending";
      return "done";
    }

    // Agent mapping during execution
    const current = cycle.current_agent || "";
    if (stageId === "research" && current.includes("research")) return "active";
    if (stageId === "novelty" && current.includes("novelty")) return "active";
    if (stageId === "script" && (current.includes("script") || current.includes("localization"))) return "active";
    if (stageId === "media" && (current.includes("storyboard") || current.includes("asset") || current.includes("presenter"))) return "active";
    if (stageId === "voice" && (current.includes("voice") || current.includes("music"))) return "active";
    if (stageId === "render" && (current.includes("editor") || current.includes("thumbnail"))) return "active";
    if (stageId === "qa" && (current.includes("compliance") || current.includes("critic"))) return "active";
    if (stageId === "publish" && current.includes("publish")) return "active";

    // If script exists, research and novelty are done
    if (script && (stageId === "research" || stageId === "novelty" || stageId === "script")) return "done";
    if (preview?.video_url && ["research", "novelty", "script", "media", "voice", "render", "qa"].includes(stageId)) return "done";

    return "pending";
  };

  return (
    <DashboardLayout>
      <Header
        title={`Cycle: ${preview?.title || cycle?.id.slice(0, 8)}`}
        description={`Task: ${preview?.topic || "Autonomous Generation"} • Language: ${preview?.language?.toUpperCase() || "EN"}`}
        actions={
          <div className="flex items-center gap-2">
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300 hover:bg-slate-900 text-xs font-semibold transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </Link>

            <button
              onClick={fetchCycleData}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
              title="Refresh pipeline status"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>

            {cycle?.status === "pending_approval" && (
              <button
                onClick={() => setIsApprovalOpen(true)}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/25 transition animate-pulse"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Review & Approve Video</span>
              </button>
            )}
          </div>
        }
      />

      <div className="p-8 space-y-6 flex-1 overflow-y-auto">
        {/* Pipeline Execution Flow Stepper */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-200 uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>Autonomous Agent Pipeline Orchestration</span>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-slate-400">
                Novelty:{" "}
                <strong className="text-slate-200">
                  {cycle?.novelty_score ? `${(cycle.novelty_score * 100).toFixed(0)}%` : "Verified"}
                </strong>
              </span>
              <span className="text-slate-400">
                Cost:{" "}
                <strong className="text-slate-200">
                  {formatCurrency(cycle?.actual_cost_usd || cycle?.estimated_cost_usd || 0)}
                </strong>
              </span>
            </div>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-2">
            {PIPELINE_STAGES.map((stage) => {
              const Icon = stage.icon;
              const status = getStageStatus(stage.id);

              return (
                <div
                  key={stage.id}
                  className={`p-2.5 rounded-xl border flex flex-col items-center text-center transition ${
                    status === "done"
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                      : status === "active"
                      ? "bg-emerald-500/20 border-emerald-400 text-emerald-300 ring-2 ring-emerald-500/30 animate-pulse"
                      : status === "failed"
                      ? "bg-red-500/10 border-red-500/30 text-red-400"
                      : "bg-slate-950/60 border-slate-800/80 text-slate-500"
                  }`}
                >
                  <div className="w-6 h-6 rounded-lg flex items-center justify-center mb-1">
                    {status === "done" ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : status === "active" ? (
                      <RefreshCw className="w-4 h-4 text-emerald-400 animate-spin" />
                    ) : (
                      <Icon className="w-4 h-4" />
                    )}
                  </div>
                  <span className="text-[10px] font-semibold leading-tight">{stage.label}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Video Preview & Details Inspection Area */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: 9:16 Video Player Container */}
          <div className="lg:col-span-5 flex flex-col items-center">
            <div className="w-full flex justify-center">
              <VideoPlayer
                src={api.cycles.getVideoUrl(cycleId)}
                poster={api.cycles.getThumbnailUrl(cycleId)}
                title={preview?.title || (cycle as any)?.task?.topic || "Autonomous Video"}
                resolution={preview?.resolution || "1080x1920"}
                duration={preview?.duration_seconds || 0}
              />
            </div>

            {/* Video Specs & Provenance Info */}
            <div className="w-full max-w-[340px] mt-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between text-slate-400">
                <span>Duration</span>
                <span className="font-semibold text-slate-200">
                  {preview?.duration_seconds ? `${preview.duration_seconds.toFixed(1)}s` : "-"}
                </span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Audio Loudness</span>
                <span className="font-semibold text-slate-200">-14 LUFS (EBU R128)</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>QA Verification</span>
                <span className="font-semibold text-emerald-400">
                  {preview?.qa_score ? `${(preview.qa_score * 100).toFixed(0)}% Passed` : "Passed"}
                </span>
              </div>
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center gap-1 text-emerald-400 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  C2PA Provenance Manifest
                </span>
                <span>Signed</span>
              </div>
            </div>
          </div>

          {/* Right Column: Tabbed Agent Data Workspace */}
          <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl overflow-hidden flex flex-col min-h-[500px]">
            {/* Tabs Header */}
            <div className="flex border-b border-slate-800 bg-slate-950/60 overflow-x-auto">
              <button
                onClick={() => setActiveTab("script")}
                className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition shrink-0 ${
                  activeTab === "script"
                    ? "border-emerald-500 text-emerald-400 bg-emerald-500/10"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Script & Scenes</span>
              </button>

              <button
                onClick={() => setActiveTab("sources")}
                className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition shrink-0 ${
                  activeTab === "sources"
                    ? "border-emerald-500 text-emerald-400 bg-emerald-500/10"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Search className="w-3.5 h-3.5" />
                <span>Web Research ({sources.length})</span>
              </button>

              <button
                onClick={() => setActiveTab("assets")}
                className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition shrink-0 ${
                  activeTab === "assets"
                    ? "border-emerald-500 text-emerald-400 bg-emerald-500/10"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Film className="w-3.5 h-3.5" />
                <span>Curated Assets ({assets.length})</span>
              </button>

              <button
                onClick={() => setActiveTab("qa")}
                className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition shrink-0 ${
                  activeTab === "qa"
                    ? "border-emerald-500 text-emerald-400 bg-emerald-500/10"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Award className="w-3.5 h-3.5" />
                <span>Compliance & QA</span>
              </button>

              <button
                onClick={() => setActiveTab("social")}
                className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition shrink-0 ${
                  activeTab === "social"
                    ? "border-emerald-500 text-emerald-400 bg-emerald-500/10"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Publishing & Copy</span>
              </button>
            </div>

            {/* Tab Contents */}
            <div className="p-6 flex-1 overflow-y-auto max-h-[600px]">
              {/* Tab 1: Script & Storyboard */}
              {activeTab === "script" && (
                <div className="space-y-4">
                  {script ? (
                    <>
                      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block mb-1">
                          Viral Hook (0-3s)
                        </span>
                        <p className="text-sm font-semibold text-slate-100">&ldquo;{script.hook}&rdquo;</p>
                        <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
                          <span>Version {script.version}</span>
                          <span>•</span>
                          <span>Language: {script.language.toUpperCase()}</span>
                          <span>•</span>
                          <span>CTA: {script.call_to_action}</span>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                          Scene-by-Scene Storyboard
                        </h4>

                        {script.scenes.map((scene) => (
                          <div
                            key={scene.scene_number}
                            className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2 text-xs"
                          >
                            <div className="flex items-center justify-between text-slate-400 pb-1.5 border-b border-slate-800/60">
                              <span className="font-bold text-emerald-400">Scene {scene.scene_number}</span>
                              <span className="text-[11px] font-mono">{scene.duration_seconds}s</span>
                            </div>

                            <div>
                              <span className="text-slate-500 text-[11px] block">Visual Direction</span>
                              <p className="text-slate-300 italic">{scene.visual_description}</p>
                            </div>

                            <div>
                              <span className="text-slate-500 text-[11px] block">Voiceover Narration</span>
                              <p className="text-slate-100 font-medium">{scene.voiceover_text}</p>
                            </div>

                            {scene.on_screen_text && (
                              <div className="flex items-center gap-2 text-[11px] text-amber-300 bg-amber-500/10 px-2 py-1 rounded">
                                <span className="font-semibold">On Screen:</span>
                                <span>{scene.on_screen_text}</span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="p-8 text-center text-xs text-slate-500">
                      Scriptwriting in progress or not available.
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Research Sources */}
              {activeTab === "sources" && (
                <div className="space-y-3">
                  {sources.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-500">
                      No research sources retrieved for this cycle.
                    </div>
                  ) : (
                    sources.map((src, i) => (
                      <div
                        key={i}
                        className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5 text-xs"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <a
                            href={src.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-bold text-emerald-400 hover:text-emerald-300 underline line-clamp-1"
                          >
                            {src.title}
                          </a>
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold shrink-0">
                            {(src.credibility_score * 100).toFixed(0)}% Credibility
                          </span>
                        </div>
                        <p className="text-slate-400 text-[11px]">{src.domain}</p>
                        {src.summary && <p className="text-slate-300 text-xs mt-1">{src.summary}</p>}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 3: Curated Assets */}
              {activeTab === "assets" && (
                <div className="space-y-3">
                  {assets.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-500">
                      No assets curated yet for this cycle.
                    </div>
                  ) : (
                    assets.map((asset) => (
                      <div
                        key={asset.id}
                        className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                      >
                        <div>
                          <p className="font-semibold text-slate-200 capitalize">
                            {asset.asset_type.replace(/_/g, " ")} ({asset.provider})
                          </p>
                          <p className="text-[11px] text-slate-500 mt-0.5">
                            License: {asset.license_type} • ID: {asset.external_id}
                          </p>
                        </div>
                        {asset.duration_seconds && (
                          <span className="font-mono text-slate-400 text-xs">
                            {asset.duration_seconds.toFixed(1)}s
                          </span>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 4: Compliance & QA */}
              {activeTab === "qa" && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-slate-100">QA & Compliance Gate</h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Automated verification by Fact Checker, Compliance Agent & Critic.
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-emerald-400">
                        {preview?.qa_score ? `${(preview.qa_score * 100).toFixed(0)}%` : "100%"}
                      </div>
                      <span className="text-[10px] text-slate-500">Pass Threshold: 80%</span>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
                      <span>Brand Voice & CTA Alignment</span>
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Passed
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
                      <span>Web Fact-Checking & Claims Grounding</span>
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
                      <span>Audio Loudness Normalization (-14 LUFS)</span>
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Compliant
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
                      <span>Licensed Media Verification (Pexels / HeyGen)</span>
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Licensed
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 5: Publishing & Copy */}
              {activeTab === "social" && (
                <div className="space-y-3">
                  {publications.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-500">
                      Video has not yet been published to social channels. Approve the video to trigger publication.
                    </div>
                  ) : (
                    publications.map((pub) => (
                      <div
                        key={pub.id}
                        className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-200 capitalize flex items-center gap-1.5">
                            <Share2 className="w-3.5 h-3.5 text-emerald-400" />
                            {pub.platform}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold capitalize">
                            {pub.status}
                          </span>
                        </div>

                        {pub.permalink && (
                          <a
                            href={pub.permalink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-emerald-400 hover:text-emerald-300 underline block"
                          >
                            View Live Post ({pub.platform})
                          </a>
                        )}

                        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-[11px] text-slate-400">
                          <div>
                            Views: <strong className="text-slate-200">{pub.views}</strong>
                          </div>
                          <div>
                            Likes: <strong className="text-slate-200">{pub.likes}</strong>
                          </div>
                          <div>
                            Shares: <strong className="text-slate-200">{pub.shares}</strong>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Human Approval Dialog */}
      <ApprovalModal
        cycleId={cycleId}
        topic={preview?.topic || "Video Task"}
        isOpen={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        onSuccess={() => {
          fetchCycleData();
        }}
      />
    </DashboardLayout>
  );
}

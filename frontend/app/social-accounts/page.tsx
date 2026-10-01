"use client";

import React, { useEffect, useState } from "react";
import {
  Share2,
  CheckCircle2,
  XCircle,
  Sparkles,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Video,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { api } from "@/lib/api";
import { SocialAccount } from "@/types";

const PLATFORMS = [
  {
    id: "youtube",
    name: "YouTube Shorts",
    description: "Publish 9:16 vertical videos directly to YouTube Shorts with SEO tags and hashtags.",
    color: "from-red-600 to-rose-600",
  },
  {
    id: "instagram",
    name: "Instagram Reels",
    description: "Post automated reels directly to Instagram Professional Creator accounts.",
    color: "from-pink-600 to-purple-600",
  },
  {
    id: "tiktok",
    name: "TikTok",
    description: "Direct video share and scheduled uploads to your TikTok creator feed.",
    color: "from-cyan-600 to-blue-600",
  },
];

export default function SocialAccountsPage() {
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const res = await api.socialAccounts.list();
      setAccounts(res);
    } catch (err) {
      console.error("Failed to load social accounts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleToggle = async (platformId: string, currentConnected: boolean) => {
    try {
      setConnectingPlatform(platformId);
      if (currentConnected) {
        await api.socialAccounts.disconnect(platformId);
      } else {
        await api.socialAccounts.connect(platformId, `@reelai_${platformId}`);
      }
      await fetchAccounts();
    } catch (err: any) {
      alert(err?.message || "Failed to update channel status");
    } finally {
      setConnectingPlatform(null);
    }
  };

  return (
    <DashboardLayout>
      <Header
        title="Connected Social Channels"
        description="Configure target platforms for automated publishing upon video approval."
        actions={
          <button
            onClick={fetchAccounts}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition"
            title="Refresh channels"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        }
      />

      <div className="p-8 space-y-6 flex-1 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLATFORMS.map((platform) => {
            const acc = accounts.find((a) => a.platform.toLowerCase() === platform.id);
            const isConnected = acc?.connected || false;
            const isProcessing = connectingPlatform === platform.id;

            return (
              <div
                key={platform.id}
                className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-slate-700/80 transition"
              >
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${platform.color} flex items-center justify-center shadow-lg text-white font-bold text-sm`}
                    >
                      <Share2 className="w-5 h-5" />
                    </div>

                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${
                        isConnected
                          ? "bg-emerald-500/15 border border-emerald-500/30 text-emerald-400"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {isConnected ? (
                        <>
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          <span>Connected</span>
                        </>
                      ) : (
                        <span>Disconnected</span>
                      )}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-100 mb-1">{platform.name}</h3>
                  <p className="text-xs text-slate-400 mb-4">{platform.description}</p>

                  {isConnected && (
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 space-y-1 text-xs">
                      <div className="flex items-center justify-between text-slate-400">
                        <span>Account:</span>
                        <span className="font-semibold text-slate-200">{acc?.account_name}</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-400">
                        <span>Status:</span>
                        <span className="text-emerald-400 font-semibold">Active & Synced</span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800">
                  <button
                    onClick={() => handleToggle(platform.id, isConnected)}
                    disabled={isProcessing}
                    className={`w-full py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 disabled:opacity-50 ${
                      isConnected
                        ? "bg-slate-800 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/30 border border-slate-700 text-slate-300"
                        : "bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/25"
                    }`}
                  >
                    {isProcessing ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : isConnected ? (
                      <span>Disconnect Channel</span>
                    ) : (
                      <span>Connect {platform.name}</span>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="text-xs text-slate-400">
            <strong>Mock Mode Active:</strong> In local development mode, connecting social accounts simulates successful OAuth handshakes and generates synthetic engagement telemetry without live third-party API credentials.
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}

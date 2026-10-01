"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Sparkles,
  Layers,
  Globe2,
  Video,
  Share2,
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle2,
  Check,
  User,
  Users,
} from "lucide-react";
import { DashboardLayout } from "@/components/common/DashboardLayout";
import { Header } from "@/components/common/Header";
import { api } from "@/lib/api";

import { AVATARS, AvatarPersona } from "@/lib/avatars";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi (हिंदी)" },
  { code: "es", label: "Spanish (Español)" },
  { code: "fr", label: "French (Français)" },
  { code: "de", label: "German (Deutsch)" },
];

const PLATFORMS = [
  { id: "youtube", label: "YouTube Shorts" },
  { id: "instagram", label: "Instagram Reels" },
  { id: "tiktok", label: "TikTok" },
];

export default function NewTaskPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [name, setName] = useState("");
  const [topic, setTopic] = useState("");
  const [seedScript, setSeedScript] = useState("");
  const [language, setLanguage] = useState("en");
  const [targetPlatforms, setTargetPlatforms] = useState<string[]>(["youtube", "instagram", "tiktok"]);

  // Presenter Config
  const [avatarId, setAvatarId] = useState("avatar_tech_alex");
  const [voiceId, setVoiceId] = useState("onyx");
  const [layout, setLayout] = useState("pip");
  const [genderFilter, setGenderFilter] = useState<"all" | "male" | "female">("all");

  const filteredAvatars = AVATARS.filter(
    (a) => genderFilter === "all" || a.gender === genderFilter
  );
  const selectedAvatar = AVATARS.find((a) => a.id === avatarId) || AVATARS[0];

  const handleSelectAvatar = (persona: AvatarPersona) => {
    setAvatarId(persona.id);
    setVoiceId(persona.defaultVoice);
  };

  // Schedule Config
  const [frequency, setFrequency] = useState("daily");
  const [time, setTime] = useState("09:00");
  const [timezone, setTimezone] = useState("UTC");

  // Brand Preferences
  const [tone, setTone] = useState("urgent and energetic");
  const [callToAction, setCallToAction] = useState("Follow for more AI breakdowns!");

  const togglePlatform = (p: string) => {
    if (targetPlatforms.includes(p)) {
      if (targetPlatforms.length > 1) {
        setTargetPlatforms(targetPlatforms.filter((item) => item !== p));
      }
    } else {
      setTargetPlatforms([...targetPlatforms, p]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !topic) {
      setError("Please fill in both Task Name and Topic.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await api.tasks.create({
        name,
        topic,
        seed_script: seedScript || undefined,
        language,
        target_platforms: targetPlatforms,
        presenter_config: {
          avatar_id: avatarId,
          voice_id: voiceId,
          layout,
        },
        schedule_config: {
          frequency,
          time,
          timezone,
          active_days: ["mon", "tue", "wed", "thu", "fri"],
        },
        brand_preferences: {
          tone,
          call_to_action: callToAction,
        },
      });

      router.push("/tasks");
    } catch (err: any) {
      setError(err?.message || "Failed to create content task.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <Header
        title="Create Content Task"
        description="Configure an autonomous video generation pipeline for your niche or brand."
        actions={
          <Link
            href="/tasks"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300 hover:bg-slate-900 text-xs font-semibold transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Tasks</span>
          </Link>
        }
      />

      <div className="p-8 max-w-4xl space-y-6 flex-1 overflow-y-auto">
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{typeof error === "string" ? error : JSON.stringify(error)}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Card 1: Content & Topic */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <Layers className="w-4 h-4" />
              <span>Step 1: Content & Niche</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Task Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Daily Tech AI Breakthroughs"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Video Language <span className="text-red-400">*</span>
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Target Topic / Angle <span className="text-red-400">*</span>
              </label>
              <textarea
                rows={2}
                required
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. DeepSeek and open weights models reshaping AI developer productivity"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                The Trend Scout and Web Researcher agents will search for real-time news matching this angle.
              </p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Optional Seed Script / Bullet Points
              </label>
              <textarea
                rows={2}
                value={seedScript}
                onChange={(e) => setSeedScript(e.target.value)}
                placeholder="Optional points or mandatory facts the Scriptwriter must cover..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Card 2: Presenter & Avatar */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-teal-400 text-xs font-bold uppercase tracking-wider">
                <Video className="w-4 h-4" />
                <span>Step 2: Studio Presenter Persona & Audio</span>
              </div>

              {/* Gender Filter Tabs */}
              <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
                <button
                  type="button"
                  onClick={() => setGenderFilter("all")}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                    genderFilter === "all"
                      ? "bg-slate-800 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5" />
                    <span>All ({AVATARS.length})</span>
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setGenderFilter("male")}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                    genderFilter === "male"
                      ? "bg-blue-600/30 text-blue-300 border border-blue-500/40 shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-blue-400" />
                    <span>Male ({AVATARS.filter((a) => a.gender === "male").length})</span>
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setGenderFilter("female")}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                    genderFilter === "female"
                      ? "bg-rose-600/30 text-rose-300 border border-rose-500/40 shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-rose-400" />
                    <span>Female ({AVATARS.filter((a) => a.gender === "female").length})</span>
                  </span>
                </button>
              </div>
            </div>

            {/* Visual Presenter Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
              {filteredAvatars.map((persona) => {
                const isSelected = avatarId === persona.id;
                const isMale = persona.gender === "male";
                return (
                  <div
                    key={persona.id}
                    onClick={() => handleSelectAvatar(persona)}
                    className={`relative cursor-pointer rounded-xl p-3.5 transition-all border text-left flex flex-col justify-between ${
                      isSelected
                        ? "bg-slate-800/80 shadow-lg scale-[1.01]"
                        : "bg-slate-950/60 hover:bg-slate-800/40 border-slate-800/80 hover:border-slate-700"
                    }`}
                    style={{
                      borderColor: isSelected ? persona.accentHex : undefined,
                      boxShadow: isSelected ? `0 0 15px -3px ${persona.accentHex}40` : undefined,
                    }}
                  >
                    <div>
                      {/* Avatar Photo + Gender Badge Header */}
                      <div className="flex items-center gap-3 mb-2.5">
                        <div className="relative w-12 h-12 rounded-xl overflow-hidden bg-slate-900 border border-slate-700 flex-shrink-0">
                          <img
                            src={persona.thumbnail}
                            alt={persona.name}
                            className="w-full h-full object-cover"
                          />
                          {isSelected && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-[1px]">
                              <div
                                className="w-5 h-5 rounded-full flex items-center justify-center text-white shadow-sm"
                                style={{ backgroundColor: persona.accentHex }}
                              >
                                <Check className="w-3 h-3 stroke-[3]" />
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-1">
                            <h4 className="text-sm font-bold text-slate-100 truncate">
                              {persona.name}
                            </h4>
                            <span
                              className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                                isMale
                                  ? "bg-blue-500/10 text-blue-400 border-blue-500/30"
                                  : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                              }`}
                            >
                              {persona.gender}
                            </span>
                          </div>
                          <p className="text-[11px] font-medium text-slate-400 truncate mt-0.5">
                            {persona.title}
                          </p>
                        </div>
                      </div>

                      <div className="text-[10px] text-slate-300 font-medium px-2 py-1 rounded bg-slate-900/90 border border-slate-800/80 mb-2 truncate">
                        {persona.badge}
                      </div>

                      <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                        {persona.description}
                      </p>
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500">
                      <span>Default Voice:</span>
                      <span className="font-semibold text-slate-300 capitalize">{persona.defaultVoice}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Layout and Voice Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 border-t border-slate-800">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Presenter Framing & Layout
                </label>
                <select
                  value={layout}
                  onChange={(e) => setLayout(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                >
                  <option value="pip">Picture-in-Picture (Lower Third Live Broadcast Badge)</option>
                  <option value="split">Split Screen (Presenter Studio + Dynamic B-Roll)</option>
                  <option value="background">Presenter Centered (Full Vertical Anchor)</option>
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-medium text-slate-300">
                    Neural Voice Model
                  </label>
                  {selectedAvatar && (
                    <span className="text-[11px] text-teal-400">
                      Recommended: <span className="font-semibold capitalize">{selectedAvatar.defaultVoice}</span>
                    </span>
                  )}
                </div>
                <select
                  value={voiceId}
                  onChange={(e) => setVoiceId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                >
                  <optgroup label="Male Voices">
                    <option value="onyx">Onyx — Deep Broadcast Baritone (Male - Recommended for News & Tech)</option>
                    <option value="echo">Echo — Smooth & Confident Explainer (Male - Recommended for Markets)</option>
                    <option value="fable">Fable — Expressive Storyteller (Male - British Accent)</option>
                    <option value="en-US-GuyNeural">Guy — Dynamic American Podcaster (Male Neural)</option>
                    <option value="hi-IN-MadhurNeural">Madhur — Indian English & Hindi (Male Neural)</option>
                  </optgroup>
                  <optgroup label="Female Voices">
                    <option value="nova">Nova — Energetic & Engaging Host (Female - Recommended for Anchors)</option>
                    <option value="shimmer">Shimmer — Crisp Studio Narrator (Female - Recommended for Culture)</option>
                    <option value="alloy">Alloy — Balanced Modern Tech Keynote (Female / Neutral)</option>
                    <option value="en-US-AriaNeural">Aria — Conversational Broadcast Explainer (Female Neural)</option>
                    <option value="hi-IN-SwaraNeural">Swara — Indian English & Hindi (Female Neural)</option>
                  </optgroup>
                </select>
              </div>
            </div>
          </div>


          {/* Card 3: Publishing & Brand */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
              <Share2 className="w-4 h-4" />
              <span>Step 3: Social Channels & Tone</span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">Target Platforms</label>
              <div className="flex flex-wrap gap-3">
                {PLATFORMS.map((plat) => {
                  const isSelected = targetPlatforms.includes(plat.id);
                  return (
                    <button
                      type="button"
                      key={plat.id}
                      onClick={() => togglePlatform(plat.id)}
                      className={`px-4 py-2 rounded-xl text-xs font-semibold border flex items-center gap-2 transition ${
                        isSelected
                          ? "bg-emerald-500/15 border-emerald-500 text-emerald-300"
                          : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                      <span>{plat.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Brand Tone</label>
                <input
                  type="text"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  placeholder="e.g. urgent, witty, educational"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Call to Action (CTA)</label>
                <input
                  type="text"
                  value={callToAction}
                  onChange={(e) => setCallToAction(e.target.value)}
                  placeholder="e.g. Drop your thoughts in the comments!"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
          </div>

          {/* Card 4: Autonomous Schedule & Post Timing */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
              <Clock className="w-4 h-4" />
              <span>Step 4: Autonomous Schedule & Post Share Timing</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Posting Frequency</label>
                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
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
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Timezone</label>
                <select
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
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
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-end gap-3 pt-4">
            <Link
              href="/tasks"
              className="px-5 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
            >
              Cancel
            </Link>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 transition flex items-center gap-2 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? "Creating Task..." : "Save & Activate Task"}</span>
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}

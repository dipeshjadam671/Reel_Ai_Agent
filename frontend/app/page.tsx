"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Sparkles, ArrowRight } from "lucide-react";

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }
  }, [user, isLoading, router]);

  // Fallback timer: ensure the user is never stuck on splash screen
  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
        if (token && token !== "undefined" && token !== "null" && token.trim()) {
          router.replace("/dashboard");
        } else {
          router.replace("/login");
        }
      } catch (e) {
        router.replace("/login");
      }
    }, 1500);
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#070A11] text-slate-100 px-4">
      <div className="flex items-center gap-2.5 text-emerald-400 font-semibold mb-3 animate-pulse">
        <Sparkles className="w-5 h-5" />
        <span className="text-base tracking-wide">Initializing ReelAI Studio...</span>
      </div>
      <p className="text-xs text-slate-500 mb-4">Connecting to studio services and workspace...</p>
      
      <div className="flex items-center gap-3 mt-2">
        <Link
          href="/dashboard"
          className="px-3.5 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-medium flex items-center gap-1.5 transition"
        >
          <span>Go to Dashboard</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
        <Link
          href="/login"
          className="px-3.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition"
        >
          Sign In
        </Link>
      </div>
    </div>
  );
}

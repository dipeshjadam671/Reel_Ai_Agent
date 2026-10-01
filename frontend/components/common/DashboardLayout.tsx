"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Sidebar } from "@/components/common/Sidebar";
import { Sparkles } from "lucide-react";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#070A11]">
        <div className="flex items-center gap-2 text-emerald-400 font-semibold animate-pulse">
          <Sparkles className="w-5 h-5" />
          <span>Loading workspace...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#070A11] flex">
      <Sidebar />
      <div className="pl-64 flex-1 flex flex-col min-w-0">
        {children}
      </div>
    </div>
  );
}

import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

export const metadata: Metadata = {
  title: "ReelAI Studio - Autonomous AI Video Generation & Publishing Platform",
  description: "Enterprise multi-tenant autonomous AI video agent platform powered by LangGraph.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#070A11] text-slate-100 min-h-screen antialiased selection:bg-emerald-500/30 selection:text-emerald-200">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}

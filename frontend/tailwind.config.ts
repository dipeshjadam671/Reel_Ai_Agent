import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#070A11",
        surface: "#0E1424",
        surfaceLight: "#162035",
        primary: "#10B981",
        primaryHover: "#059669",
        accent: "#06B6D4",
        accentWarning: "#F59E0B",
        accentDanger: "#EF4444",
      },
    },
  },
  plugins: [],
};
export default config;

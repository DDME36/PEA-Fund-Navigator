import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        space: ["var(--font-space)", "sans-serif"],
        thai: ["var(--font-thai)", "sans-serif"],
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        border: "hsl(var(--border))",
        bullish: "#22c55e",
        bearish: "#ef4444",
        aqua: {
          50: "#e0ffff",
          100: "#b8ffff",
          200: "#7fffff",
          300: "#40e0d0",
          400: "#00ced1",
          500: "#00bcd4",
          600: "#00acc1",
          700: "#0097a7",
          800: "#00838f",
          900: "#006064",
        },
        flux: {
          pink: "#ff6b9d",
          purple: "#c084fc",
          blue: "#60a5fa",
          cyan: "#22d3ee",
          teal: "#2dd4bf",
          mint: "#6ee7b7",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        "aqua-pulse": "aqua-pulse 4s ease-in-out infinite",
        "flux-flow": "flux-flow 6s ease infinite",
        "glow-pulse": "glow-pulse 3s ease-in-out infinite",
        "float": "float 5s ease-in-out infinite",
        "shimmer": "shimmer 2s ease-in-out infinite",
        "wave": "wave 3s ease-in-out infinite",
        "aurora": "aurora 10s ease infinite",
      },
      keyframes: {
        "aqua-pulse": {
          "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
          "50%": { opacity: "0.8", transform: "scale(1.1)" },
        },
        "flux-flow": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(0, 206, 209, 0.4), 0 0 40px rgba(0, 206, 209, 0.2)" },
          "50%": { boxShadow: "0 0 40px rgba(0, 206, 209, 0.6), 0 0 80px rgba(0, 206, 209, 0.3)" },
        },
        "float": {
          "0%, 100%": { transform: "translateY(0px) rotate(0deg)" },
          "25%": { transform: "translateY(-8px) rotate(1deg)" },
          "75%": { transform: "translateY(-4px) rotate(-1deg)" },
        },
        "shimmer": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        "wave": {
          "0%, 100%": { transform: "translateY(0) scaleY(1)" },
          "50%": { transform: "translateY(-5px) scaleY(1.05)" },
        },
        "aurora": {
          "0%, 100%": { backgroundPosition: "0% 50%", filter: "hue-rotate(0deg)" },
          "50%": { backgroundPosition: "100% 50%", filter: "hue-rotate(30deg)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;

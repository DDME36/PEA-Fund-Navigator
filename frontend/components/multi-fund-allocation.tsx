"use client";

import { useState } from "react";
import type { MultiFundAllocation } from "@/lib/types";

interface MultiFundAllocationProps {
  conservative: MultiFundAllocation;
  moderate: MultiFundAllocation;
  aggressive: MultiFundAllocation;
}

const FUND_COLORS = {
  "PEA-F": "#f472b6", // Pink (Bond)
  "PEA-E": "#22d3ee", // Cyan (Thai Equity)
  "PEA-G": "#a78bfa", // Purple (Global Equity)
  "PEA-P": "#fb923c", // Orange (Property/REITs)
};

const FUND_NAMES = {
  "PEA-F": "ตราสารหนี้",
  "PEA-E": "หุ้นไทย",
  "PEA-G": "หุ้นต่างประเทศ",
  "PEA-P": "อสังหาฯ/REITs",
};

const FUND_ICONS = {
  "PEA-F": "🛡️",
  "PEA-E": "🇹🇭",
  "PEA-G": "🌍",
  "PEA-P": "🏢",
};

export function MultiFundAllocation({
  conservative,
  moderate,
  aggressive,
}: MultiFundAllocationProps) {
  const [selectedProfile, setSelectedProfile] = useState<"conservative" | "moderate" | "aggressive">("moderate");

  const profiles = {
    conservative: { name: "ปลอดภัย", allocation: conservative, icon: "🛡️", desc: "เน้นความมั่นคง" },
    moderate: { name: "ปกติ", allocation: moderate, icon: "⚖️", desc: "สมดุล" },
    aggressive: { name: "ดุดัน", allocation: aggressive, icon: "🚀", desc: "เน้นผลตอบแทน" },
  };

  const currentAllocation = profiles[selectedProfile].allocation;

  return (
    <div className="space-y-4">
      {/* Profile Selector */}
      <div className="flex gap-2 justify-center">
        {(Object.keys(profiles) as Array<keyof typeof profiles>).map((key) => (
          <button
            key={key}
            onClick={() => setSelectedProfile(key)}
            className={`px-3 py-2 rounded-lg text-xs sm:text-sm transition-all ${
              selectedProfile === key
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50"
                : "bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 border border-zinc-700/50"
            }`}
          >
            <div className="flex items-center gap-1.5">
              <span>{profiles[key].icon}</span>
              <span className="font-medium">{profiles[key].name}</span>
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">{profiles[key].desc}</div>
          </button>
        ))}
      </div>

      {/* Allocation Bars */}
      <div className="space-y-2">
        {(Object.keys(currentAllocation) as Array<keyof MultiFundAllocation>).map((fund) => {
          const percentage = currentAllocation[fund];
          return (
            <div key={fund} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-300 flex items-center gap-1.5">
                  <span>{FUND_ICONS[fund]}</span>
                  <span>{fund}</span>
                  <span className="text-zinc-500 text-[10px]">({FUND_NAMES[fund]})</span>
                </span>
                <span className="font-medium tabular-nums" style={{ color: FUND_COLORS[fund] }}>
                  {percentage}%
                </span>
              </div>
              <div className="h-2 bg-zinc-800/50 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-700 rounded-full"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: FUND_COLORS[fund],
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Pie Chart */}
      <div className="flex justify-center pt-2">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            {(() => {
              let offset = 0;
              return (Object.keys(currentAllocation) as Array<keyof MultiFundAllocation>).map((fund) => {
                const percentage = currentAllocation[fund];
                const dashArray = `${percentage * 2.51} 251`;
                const dashOffset = -offset * 2.51;
                offset += percentage;
                return (
                  <circle
                    key={fund}
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke={FUND_COLORS[fund]}
                    strokeWidth="20"
                    strokeDasharray={dashArray}
                    strokeDashoffset={dashOffset}
                    className="transition-all duration-700"
                  />
                );
              });
            })()}
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl">{profiles[selectedProfile].icon}</div>
              <div className="text-[10px] text-zinc-400 mt-1">{profiles[selectedProfile].name}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-2 text-[10px] pt-2 border-t border-zinc-800/50">
        {(Object.keys(currentAllocation) as Array<keyof MultiFundAllocation>).map((fund) => (
          <div key={fund} className="flex items-center gap-1.5">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: FUND_COLORS[fund] }}
            />
            <span className="text-zinc-400">{fund}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

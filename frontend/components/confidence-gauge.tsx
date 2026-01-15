"use client";

import { cn } from "@/lib/utils";

interface ConfidenceGaugeProps {
  value: number;
  isBullish: boolean;
}

export function ConfidenceGauge({ value, isBullish }: ConfidenceGaugeProps) {
  const percentage = Math.round(value * 100);
  const rotation = (value * 180) - 90;
  
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-48 h-24 overflow-hidden">
        {/* Background arc */}
        <div className="absolute inset-0 rounded-t-full border-8 border-muted" />
        
        {/* Colored arc */}
        <div
          className={cn(
            "absolute inset-0 rounded-t-full border-8 transition-all duration-700",
            isBullish ? "border-bullish" : "border-bearish"
          )}
          style={{
            clipPath: `polygon(0 100%, 0 0, ${value * 100}% 0, ${value * 100}% 100%)`,
          }}
        />
        
        {/* Needle */}
        <div
          className="absolute bottom-0 left-1/2 w-1 h-20 origin-bottom transition-transform duration-700"
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        >
          <div className={cn(
            "w-full h-full rounded-full",
            isBullish ? "bg-bullish" : "bg-bearish"
          )} />
        </div>
        
        {/* Center dot */}
        <div className={cn(
          "absolute bottom-0 left-1/2 w-4 h-4 -translate-x-1/2 translate-y-1/2 rounded-full",
          isBullish ? "bg-bullish" : "bg-bearish"
        )} />
      </div>
      
      {/* Value display */}
      <div className="text-center">
        <span className={cn(
          "text-4xl font-bold",
          isBullish ? "text-bullish" : "text-bearish"
        )}>
          {percentage}%
        </span>
        <p className="text-sm text-muted-foreground mt-1">Confidence Level</p>
      </div>
    </div>
  );
}

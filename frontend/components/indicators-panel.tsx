"use client";

import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { cn } from "@/lib/utils";
import type { IndicatorsResponse } from "@/lib/types";

interface IndicatorsPanelProps {
  data: IndicatorsResponse;
}

export function IndicatorsPanel({ data }: IndicatorsPanelProps) {
  const { indicators, close } = data;
  
  const rsiStatus = indicators.RSI > 70 ? "overbought" : indicators.RSI < 30 ? "oversold" : "neutral";
  const macdStatus = indicators.MACD > indicators.MACD_Signal ? "bullish" : "bearish";
  const smaStatus = close > indicators.SMA_50 && indicators.SMA_50 > indicators.SMA_200 ? "bullish" : "bearish";
  
  return (
    <Card className="bg-card/50 backdrop-blur">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>📊</span>
          Technical Indicators
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <IndicatorItem
            name="RSI (14)"
            value={indicators.RSI.toFixed(2)}
            status={rsiStatus}
            description={rsiStatus === "overbought" ? "Overbought" : rsiStatus === "oversold" ? "Oversold" : "Neutral"}
          />
          <IndicatorItem
            name="MACD"
            value={indicators.MACD.toFixed(4)}
            status={macdStatus}
            description={`Signal: ${indicators.MACD_Signal.toFixed(4)}`}
          />
          <IndicatorItem
            name="SMA 50"
            value={indicators.SMA_50.toFixed(2)}
            status={close > indicators.SMA_50 ? "bullish" : "bearish"}
            description={close > indicators.SMA_50 ? "Price above" : "Price below"}
          />
          <IndicatorItem
            name="SMA 200"
            value={indicators.SMA_200.toFixed(2)}
            status={close > indicators.SMA_200 ? "bullish" : "bearish"}
            description={close > indicators.SMA_200 ? "Price above" : "Price below"}
          />
          <IndicatorItem
            name="BB Upper"
            value={indicators.BB_Upper.toFixed(2)}
            status="neutral"
            description="Bollinger Band"
          />
          <IndicatorItem
            name="BB Lower"
            value={indicators.BB_Lower.toFixed(2)}
            status="neutral"
            description="Bollinger Band"
          />
        </div>
        
        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Current Price</span>
            <span className="text-lg font-bold">{close.toFixed(2)} THB</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface IndicatorItemProps {
  name: string;
  value: string;
  status: "bullish" | "bearish" | "neutral" | "overbought" | "oversold";
  description: string;
}

function IndicatorItem({ name, value, status, description }: IndicatorItemProps) {
  return (
    <div className="p-3 rounded-lg bg-muted/50">
      <div className="flex justify-between items-start">
        <span className="text-sm text-muted-foreground">{name}</span>
        <span className={cn(
          "text-xs px-2 py-0.5 rounded-full",
          status === "bullish" && "bg-bullish/20 text-bullish",
          status === "bearish" && "bg-bearish/20 text-bearish",
          status === "overbought" && "bg-orange-500/20 text-orange-400",
          status === "oversold" && "bg-blue-500/20 text-blue-400",
          status === "neutral" && "bg-muted text-muted-foreground"
        )}>
          {status}
        </span>
      </div>
      <p className="text-lg font-semibold mt-1">{value}</p>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}

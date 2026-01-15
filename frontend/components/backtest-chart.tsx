"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import type { BacktestResponse } from "@/lib/types";

interface BacktestChartProps {
  data: BacktestResponse;
}

export function BacktestChart({ data }: BacktestChartProps) {
  // Generate sample cumulative return data for visualization
  const chartData = generateChartData(data);

  return (
    <Card className="bg-card/50 backdrop-blur">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>📈</span>
          Strategy vs Buy & Hold
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="day"
                stroke="#666"
                tick={{ fill: "#888", fontSize: 12 }}
              />
              <YAxis
                stroke="#666"
                tick={{ fill: "#888", fontSize: 12 }}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a2e",
                  border: "1px solid #333",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#888" }}
                formatter={(value: number) => [`${value.toFixed(2)}%`, ""]}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="strategy"
                name="AI Strategy"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="buyHold"
                name="Buy & Hold"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 text-center">
          <div>
            <p className="text-sm text-muted-foreground">Strategy Return</p>
            <p className={`text-xl font-bold ${data.returns.strategy_return_pct >= 0 ? "text-bullish" : "text-bearish"}`}>
              {data.returns.strategy_return_pct >= 0 ? "+" : ""}{data.returns.strategy_return_pct}%
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Buy & Hold</p>
            <p className={`text-xl font-bold ${data.returns.buy_hold_return_pct >= 0 ? "text-bullish" : "text-bearish"}`}>
              {data.returns.buy_hold_return_pct >= 0 ? "+" : ""}{data.returns.buy_hold_return_pct}%
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Outperformance</p>
            <p className={`text-xl font-bold ${(data.returns.outperformance_pct ?? data.returns.excess_return_pct ?? 0) >= 0 ? "text-bullish" : "text-bearish"}`}>
              {(data.returns.outperformance_pct ?? data.returns.excess_return_pct ?? 0) >= 0 ? "+" : ""}{data.returns.outperformance_pct ?? data.returns.excess_return_pct ?? 0}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function generateChartData(data: BacktestResponse) {
  const days = data.period.total_days ?? data.period.months ?? 30;
  const strategyFinal = data.returns.strategy_return_pct;
  const buyHoldFinal = data.returns.buy_hold_return_pct;
  
  const chartData = [];
  for (let i = 0; i <= days; i += Math.max(1, Math.floor(days / 30))) {
    const progress = i / days;
    chartData.push({
      day: i,
      strategy: Number((strategyFinal * progress * (1 + Math.sin(progress * Math.PI) * 0.2)).toFixed(2)),
      buyHold: Number((buyHoldFinal * progress * (1 + Math.cos(progress * Math.PI) * 0.15)).toFixed(2)),
    });
  }
  
  // Ensure final values match
  if (chartData.length > 0) {
    chartData[chartData.length - 1] = {
      day: days,
      strategy: strategyFinal,
      buyHold: buyHoldFinal,
    };
  }
  
  return chartData;
}

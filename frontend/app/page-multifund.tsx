"use client";

import { useState, useEffect, useCallback } from "react";
import { getDailyData, formatUpdatedAt, getDataAge, type DailyData } from "@/lib/api";
import { MultiFundAllocation } from "@/components/multi-fund-allocation";

export default function Dashboard() {
  const [data, setData] = useState<DailyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    setRefreshing(true);
    setError(null);
    try {
      const result = await getDailyData();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
      setTimeout(() => setRefreshing(false), 500);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const prediction = data?.prediction;
  const backtest = data?.backtest;
  const isBullish = prediction?.prediction === "Bullish";

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-zinc-300">กำลังโหลด...</div>
      </main>
    );
  }

  if (error || !prediction) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <p className="text-zinc-300 mb-4">{error || "ยังไม่มีข้อมูล"}</p>
          <button onClick={fetchData} className="px-4 py-2 text-sm text-cyan-400 hover:text-cyan-300">
            ลองใหม่
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen relative z-10">
      <div className="max-w-md mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-6 sm:space-y-8">
        
        {/* Header */}
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-lg sm:text-xl font-semibold">PEA Fund Navigator</h1>
            <p className="text-xs text-zinc-300">นำทางกองทุนสำรองเลี้ยงชีพ (4 กอง)</p>
          </div>
          <button 
            onClick={fetchData} 
            className="p-2 text-zinc-300 hover:text-white hover:bg-zinc-800/50 rounded-lg transition-all"
          >
            <svg className={`w-5 h-5 ${refreshing ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </header>

        {/* Updated Time */}
        {data?.updated_at && (
          <div className="text-center">
            <span className="text-xs text-zinc-300">
              อัพเดท {formatUpdatedAt(data.updated_timestamp)} · {getDataAge(data.updated_timestamp)}
            </span>
          </div>
        )}

        {/* Main Prediction */}
        <section className="text-center py-6">
          <div className="text-5xl sm:text-6xl mb-4">
            {prediction.weather.split(" ")[0]}
          </div>
          <p className="text-zinc-300 text-xs mb-2">{prediction.date}</p>
          <h2 className={`text-xl sm:text-2xl font-medium mb-3 ${isBullish ? "text-cyan-400" : "text-pink-400"}`}>
            {isBullish ? "แนวโน้มขาขึ้น" : "แนวโน้มขาลง"}
          </h2>
          <div className="inline-flex items-center gap-2 text-xs text-zinc-200">
            <span className={`w-1.5 h-1.5 rounded-full ${isBullish ? "bg-cyan-400" : "bg-pink-400"}`} />
            <span>ความมั่นใจ {Math.round((prediction.probability ?? 0) * 100)}%</span>
          </div>
        </section>

        {/* Multi-Fund Allocation */}
        {prediction.multi_fund && (
          <section className="p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50">
            <h3 className="text-sm font-medium text-white mb-4 text-center">
              📊 สัดส่วนแนะนำ (เลือกโหมดความเสี่ยง)
            </h3>
            <MultiFundAllocation
              conservative={prediction.multi_fund.conservative}
              moderate={prediction.multi_fund.moderate}
              aggressive={prediction.multi_fund.aggressive}
            />
            <p className="text-[10px] text-zinc-500 text-center mt-4">
              💡 เคล็ดลับ: ระบบใช้ EMA Smoothing เพื่อลดการสวิงของสัดส่วน
            </p>
          </section>
        )}

        {/* Trend Analysis */}
        {prediction.trend && (
          <section className="p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{prediction.trend.trend_icon}</span>
                <span className="text-sm font-medium text-white">{prediction.trend.trend}</span>
              </div>
              <div className="text-xs text-zinc-400">
                คะแนน {prediction.trend.trend_score}/100
              </div>
            </div>
            
            <div className="flex gap-2 flex-wrap">
              <span className={`px-2 py-1 rounded-full text-xs ${
                prediction.trend.momentum["1m"] >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
              }`}>
                1 เดือน: {prediction.trend.momentum["1m"] > 0 ? '+' : ''}{prediction.trend.momentum["1m"]}%
              </span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                prediction.trend.momentum["3m"] >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
              }`}>
                3 เดือน: {prediction.trend.momentum["3m"] > 0 ? '+' : ''}{prediction.trend.momentum["3m"]}%
              </span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                prediction.trend.momentum["6m"] >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
              }`}>
                6 เดือน: {prediction.trend.momentum["6m"] > 0 ? '+' : ''}{prediction.trend.momentum["6m"]}%
              </span>
            </div>
          </section>
        )}

        {/* Backtest Stats */}
        {backtest && (
          <section className="pt-5 border-t border-zinc-800/50">
            <p className="text-xs text-zinc-300 mb-3">ผลการทดสอบย้อนหลัง (ML Model)</p>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 rounded-xl hover:bg-zinc-800/30 transition-colors">
                <div className="text-base font-medium">{backtest.metrics?.win_rate_pct}%</div>
                <div className="text-[10px] text-zinc-300">อัตราชนะ</div>
              </div>
              <div className="p-2 rounded-xl hover:bg-zinc-800/30 transition-colors">
                <div className={`text-base font-medium ${backtest.returns?.strategy_return_pct >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {backtest.returns?.strategy_return_pct > 0 ? "+" : ""}{backtest.returns?.strategy_return_pct}%
                </div>
                <div className="text-[10px] text-zinc-300">ผลตอบแทน</div>
              </div>
              <div className="p-2 rounded-xl hover:bg-zinc-800/30 transition-colors">
                <div className="text-base font-medium">{backtest.metrics?.sharpe_ratio}</div>
                <div className="text-[10px] text-zinc-300">ค่า Sharpe</div>
              </div>
            </div>
          </section>
        )}

      </div>
    </main>
  );
}

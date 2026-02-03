"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { getDailyData, formatUpdatedAt, getDataAge, type DailyData } from "@/lib/api";
import { MultiFundAllocation } from "@/components/multi-fund-allocation";

function useCountUp(end: number, duration = 800) {
  const [count, setCount] = useState(end);
  const prevEnd = useRef(end);
  const isFirstRender = useRef(true);
  
  useEffect(() => {
    // Skip animation on first render, just set the value
    if (isFirstRender.current) {
      isFirstRender.current = false;
      setCount(end);
      prevEnd.current = end;
      
      // Animate from 0 to end on mount
      const startTime = performance.now();
      const animate = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        setCount(Math.round(end * eased));
        if (progress < 1) requestAnimationFrame(animate);
      };
      requestAnimationFrame(animate);
      return;
    }
    
    // If value changed, animate to new value
    if (prevEnd.current !== end) {
      const startValue = prevEnd.current;
      prevEnd.current = end;
      const startTime = performance.now();
      
      const animate = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        setCount(Math.round(startValue + (end - startValue) * eased));
        if (progress < 1) requestAnimationFrame(animate);
      };
      requestAnimationFrame(animate);
    }
  }, [end, duration]);
  
  return count;
}

function usePullToRefresh(onRefresh: () => Promise<void>) {
  const [pulling, setPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const startY = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleTouchStart = (e: TouchEvent) => {
      if (window.scrollY === 0) {
        startY.current = e.touches[0].clientY;
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (window.scrollY > 0) return;
      const currentY = e.touches[0].clientY;
      const diff = currentY - startY.current;
      if (diff > 0 && diff < 150) {
        setPullDistance(diff);
        setPulling(true);
      }
    };

    const handleTouchEnd = async () => {
      if (pullDistance > 80) {
        await onRefresh();
      }
      setPullDistance(0);
      setPulling(false);
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: true });
    container.addEventListener('touchmove', handleTouchMove, { passive: true });
    container.addEventListener('touchend', handleTouchEnd);

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [pullDistance, onRefresh]);

  return { containerRef, pulling, pullDistance };
}

export default function Dashboard() {
  const [showDetails, setShowDetails] = useState(false);
  const [data, setData] = useState<DailyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [predictionKey, setPredictionKey] = useState(0);
  const prevPrediction = useRef<string | null>(null);

  useEffect(() => setMounted(true), []);

  const fetchData = useCallback(async () => {
    setRefreshing(true);
    setError(null);
    try {
      const result = await getDailyData();
      if (prevPrediction.current && prevPrediction.current !== result.prediction?.prediction) {
        setPredictionKey(k => k + 1);
      }
      prevPrediction.current = result.prediction?.prediction ?? null;
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
      setTimeout(() => setRefreshing(false), 500);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const { containerRef, pulling, pullDistance } = usePullToRefresh(fetchData);

  const prediction = data?.prediction;
  const backtest = data?.backtest;
  const isBullish = prediction?.prediction === "Bullish";
  const peaE = prediction?.recommended_allocation ?? 50;
  const peaF = 100 - peaE;
  
  const animatedPeaE = useCountUp(peaE);
  const animatedPeaF = useCountUp(peaF);
  const animatedProb = useCountUp(Math.round((prediction?.probability ?? 0) * 100));
  const animatedWinRate = useCountUp(backtest?.metrics?.win_rate_pct ?? 0);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'r' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        fetchData();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [fetchData]);

  if (loading) {
    return (
      <main className="min-h-screen relative z-10" role="main" aria-label="กำลังโหลดข้อมูล">
        <div className="max-w-md mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-6 sm:space-y-8 animate-pulse">
          <div className="flex justify-between">
            <div className="space-y-2">
              <div className="h-6 w-32 bg-zinc-800 rounded" />
              <div className="h-3 w-24 bg-zinc-800 rounded" />
            </div>
            <div className="h-9 w-9 bg-zinc-800 rounded-lg" />
          </div>
          <div className="h-4 w-40 bg-zinc-800 rounded mx-auto" />
          <div className="py-8 space-y-4">
            <div className="h-16 w-16 bg-zinc-800 rounded-full mx-auto" />
            <div className="h-4 w-24 bg-zinc-800 rounded mx-auto" />
            <div className="h-8 w-40 bg-zinc-800 rounded mx-auto" />
          </div>
          <div className="flex justify-center gap-8">
            <div className="h-32 w-32 bg-zinc-800 rounded-full" />
            <div className="space-y-3">
              <div className="h-4 w-24 bg-zinc-800 rounded" />
              <div className="h-4 w-24 bg-zinc-800 rounded" />
            </div>
          </div>
        </div>
        <span className="sr-only">กำลังโหลดข้อมูลการทำนาย</span>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 relative z-10" role="main" aria-label="เกิดข้อผิดพลาด">
        <div className="text-center" role="alert">
          <p className="text-zinc-300 mb-4">{error}</p>
          <button 
            onClick={fetchData} 
            className="px-4 py-2 text-sm text-cyan-400 hover:text-cyan-300 transition-colors focus-ring"
            aria-label="ลองโหลดข้อมูลใหม่"
          >
            ลองใหม่
          </button>
        </div>
      </main>
    );
  }

  if (!prediction) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 relative z-10" role="main">
        <div className="text-center">
          <p className="text-zinc-300 mb-4">ยังไม่มีข้อมูล</p>
          <code className="text-xs text-zinc-400">python scripts/daily_update.py</code>
        </div>
      </main>
    );
  }

  return (
    <main 
      ref={containerRef}
      className="min-h-screen min-h-[100dvh] safe-area-inset relative z-10" 
      role="main" 
      aria-label="แดชบอร์ดแนะนำสัดส่วนกองทุน"
    >
      {/* Pull to refresh indicator */}
      {pulling && (
        <div 
          className="fixed top-0 left-0 right-0 flex justify-center pt-4 pull-indicator"
          style={{ transform: `translateY(${Math.min(pullDistance - 40, 20)}px)`, opacity: pullDistance / 80 }}
          aria-hidden="true"
        >
          <div className={`w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full ${pullDistance > 80 ? 'animate-spin' : ''}`} />
        </div>
      )}

      <div className={`max-w-md mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-6 sm:space-y-8 transition-all duration-500 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
        
        {/* Header */}
        <header className="flex items-center justify-between animate-fade-in-up">
          <div>
            <h1 className="text-lg sm:text-xl font-semibold">PEA Fund Navigator</h1>
            <p className="text-xs text-zinc-300">นำทางกองทุนสำรองเลี้ยงชีพ</p>
          </div>
          <button 
            onClick={fetchData} 
            className="p-2.5 sm:p-2 text-zinc-300 hover:text-white hover:bg-zinc-800/50 rounded-lg transition-all active:scale-95 touch-manipulation focus-ring"
            aria-label="รีเฟรชข้อมูล (Ctrl+R)"
            title="รีเฟรช (Ctrl+R)"
          >
            <svg className={`w-5 h-5 transition-transform duration-500 ${refreshing ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </header>

        {/* Updated Time */}
        {data?.updated_at && (
          <div className="text-center animate-fade-in-up delay-100" aria-live="polite">
            <span className="text-[11px] sm:text-xs text-zinc-300">
              อัพเดท {formatUpdatedAt(data.updated_timestamp)} · {getDataAge(data.updated_timestamp)}
            </span>
          </div>
        )}

        {/* Main Prediction */}
        <section 
          key={predictionKey}
          className="text-center py-6 sm:py-8 animate-fade-in-up delay-200" 
          aria-label="ผลการทำนาย"
        >
          <div className="text-5xl sm:text-6xl mb-4 sm:mb-6 hover:scale-110 transition-transform cursor-default select-none" role="img" aria-label={prediction.weather}>
            {prediction.weather.split(" ")[0]}
          </div>
          <p className="text-zinc-300 text-xs sm:text-sm mb-2 sm:mb-3">{prediction.date}</p>
          <h2 className={`text-xl sm:text-2xl font-medium mb-3 sm:mb-4 ${isBullish ? "text-cyan-400" : "text-pink-400"}`}>
            {isBullish ? "แนวโน้มขาขึ้น" : "แนวโน้มขาลง"}
          </h2>
          <div className="inline-flex items-center gap-2 text-xs sm:text-sm text-zinc-200">
            <span className={`w-1.5 h-1.5 rounded-full ${isBullish ? "bg-cyan-400" : "bg-pink-400"}`} aria-hidden="true" />
            <span>ความมั่นใจ <span aria-live="polite">{animatedProb}%</span></span>
          </div>
        </section>

        {/* Trend & Recommendation */}
        {prediction.trend && (
          <section className="animate-fade-in-up delay-250" aria-label="แนวโน้มและคำแนะนำ">
            <div className="p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50">
              {/* Trend Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{prediction.trend.trend_icon}</span>
                  <span className="text-sm font-medium text-white">{prediction.trend.trend}</span>
                </div>
                <div className="text-xs text-zinc-400">
                  คะแนน {prediction.trend.trend_score}/100
                </div>
              </div>
              
              {/* Recommendation Box */}
              <div className={`p-3 rounded-xl mb-3 ${
                prediction.trend.comparison.recommendation.includes('PEA-E') 
                  ? 'bg-cyan-500/10 border border-cyan-500/20' 
                  : 'bg-pink-500/10 border border-pink-500/20'
              }`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-sm font-medium ${
                    prediction.trend.comparison.recommendation.includes('PEA-E') 
                      ? 'text-cyan-400' 
                      : 'text-pink-400'
                  }`}>
                    {prediction.trend.comparison.recommendation.includes('PEA-E') ? '💎' : '🛡️'} {prediction.trend.comparison.recommendation}
                  </span>
                </div>
                <p className="text-xs text-zinc-300">{prediction.trend.comparison.reason}</p>
              </div>
              
              {/* Momentum Pills */}
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
            </div>
          </section>
        )}

        {/* Multi-Fund Allocation (4 กอง) */}
        {prediction.multi_fund ? (
          <section className="animate-fade-in-up delay-300">
            <div className="p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50">
              <h3 className="text-sm font-medium text-white mb-4 text-center flex items-center justify-center gap-2">
                <span>📊</span>
                <span>สัดส่วนแนะนำ 4 กอง</span>
                <span className="text-xs text-zinc-500">(เลือกโหมดความเสี่ยง)</span>
              </h3>
              <MultiFundAllocation
                conservative={prediction.multi_fund.conservative}
                moderate={prediction.multi_fund.moderate}
                aggressive={prediction.multi_fund.aggressive}
              />
              <p className="text-[10px] text-zinc-500 text-center mt-4">
                💡 ระบบใช้ EMA Smoothing เพื่อลดการสวิงของสัดส่วน
              </p>
            </div>
          </section>
        ) : (
          /* Legacy 2-Fund Allocation (fallback) */
          <section className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 animate-fade-in-up delay-300" aria-label="สัดส่วนการลงทุนที่แนะนำ">
            {/* Mascot - left side on desktop */}
            <div className="mascot hidden sm:block" title="PEA Navigator Mascot">
              <img src="/mascot.png" alt="Mascot" />
            </div>
            
            <div className="relative w-28 h-28 sm:w-32 sm:h-32 group" role="img" aria-label={`PEA-E ${peaE}% PEA-F ${peaF}%`}>
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100" aria-hidden="true">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#27272a" strokeWidth="12" />
                <circle 
                  cx="50" cy="50" r="40" fill="none" 
                  stroke="#22d3ee" strokeWidth="12"
                  strokeDasharray={`${animatedPeaE * 2.51} 251`}
                  strokeLinecap="round"
                  className="transition-all duration-700"
                />
                <circle 
                  cx="50" cy="50" r="40" fill="none" 
                  stroke="#f472b6" strokeWidth="12"
                  strokeDasharray={`${animatedPeaF * 2.51} 251`}
                  strokeDashoffset={`${-animatedPeaE * 2.51}`}
                  strokeLinecap="round"
                  className="transition-all duration-700"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs text-zinc-400">สัดส่วน</span>
              </div>
            </div>
            
            <div className="flex sm:flex-col gap-6 sm:gap-3 text-sm">
              <div className="flex items-center gap-2 sm:hover:translate-x-1 transition-transform cursor-default">
                <span className="w-2 h-2 rounded-full bg-cyan-400" aria-hidden="true" />
                <span className="text-zinc-200">PEA-E <span className="text-zinc-400 text-xs">(SET50)</span></span>
                <span className="text-cyan-400 font-medium tabular-nums" aria-live="polite">{animatedPeaE}%</span>
              </div>
              <div className="flex items-center gap-2 sm:hover:translate-x-1 transition-transform cursor-default">
                <span className="w-2 h-2 rounded-full bg-pink-400" aria-hidden="true" />
                <span className="text-zinc-200">PEA-F <span className="text-zinc-400 text-xs">(Bond)</span></span>
                <span className="text-pink-400 font-medium tabular-nums" aria-live="polite">{animatedPeaF}%</span>
              </div>
            </div>
            
            {/* Mascot - below on mobile */}
            <div className="mascot sm:hidden mt-2" title="PEA Navigator Mascot">
              <img src="/mascot.png" alt="Mascot" />
            </div>
          </section>
        )}

        {/* Backtest Stats - Always visible */}
        {backtest && (
          <section className="pt-5 sm:pt-6 border-t border-zinc-800/50 animate-fade-in-up delay-400" aria-label="ผลการทดสอบย้อนหลัง">
            <p className="text-[11px] sm:text-xs text-zinc-300 mb-3 sm:mb-4">ผลทดสอบย้อนหลัง (ML Model)</p>
            <div className="grid grid-cols-3 gap-2 sm:gap-4 text-center">
              <div className="p-2 sm:p-3 rounded-xl hover:bg-zinc-800/30 transition-colors cursor-default focus-ring" tabIndex={0}>
                <div className="text-base sm:text-lg font-medium tabular-nums">{animatedWinRate}%</div>
                <div className="text-[10px] sm:text-xs text-zinc-300">อัตราชนะ</div>
              </div>
              <div className="p-2 sm:p-3 rounded-xl hover:bg-zinc-800/30 transition-colors cursor-default focus-ring" tabIndex={0}>
                <div className={`text-base sm:text-lg font-medium tabular-nums ${backtest.returns?.strategy_return_pct >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {backtest.returns?.strategy_return_pct > 0 ? "+" : ""}{backtest.returns?.strategy_return_pct}%
                </div>
                <div className="text-[10px] sm:text-xs text-zinc-300">ผลตอบแทน</div>
              </div>
              <div className="p-2 sm:p-3 rounded-xl hover:bg-zinc-800/30 transition-colors cursor-default focus-ring" tabIndex={0}>
                <div className="text-base sm:text-lg font-medium tabular-nums">{backtest.metrics?.sharpe_ratio}</div>
                <div className="text-[10px] sm:text-xs text-zinc-300">ค่า Sharpe</div>
              </div>
            </div>
            
            {/* Performance Chart */}
            {backtest.history && backtest.history.length > 0 && (
              <div className="mt-4 p-3 rounded-xl bg-zinc-900/50">
                <p className="text-[10px] sm:text-xs text-zinc-400 mb-3">
                  เปรียบเทียบผลตอบแทน {backtest.history.length} เดือน ({backtest.history[0]?.date} ถึง {backtest.history[backtest.history.length - 1]?.date})
                </p>
                
                {/* Simple Line Chart */}
                <div className="relative h-32 sm:h-40 pr-14">
                  <svg className="w-full h-full" viewBox="0 0 300 100" preserveAspectRatio="none">
                    {/* Grid lines */}
                    <line x1="0" y1="50" x2="300" y2="50" stroke="#27272a" strokeWidth="0.5" strokeDasharray="4" />
                    
                    {/* Strategy line (cyan) */}
                    <polyline
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="2"
                      points={backtest.history.map((h, i) => {
                        const x = (i / (backtest.history!.length - 1)) * 300;
                        const minVal = Math.min(...backtest.history!.map(h => Math.min(h.strategy_value, h.buyhold_value, h.bond_value)));
                        const maxVal = Math.max(...backtest.history!.map(h => Math.max(h.strategy_value, h.buyhold_value, h.bond_value)));
                        const y = 100 - ((h.strategy_value - minVal) / (maxVal - minVal)) * 100;
                        return `${x},${y}`;
                      }).join(' ')}
                    />
                    
                    {/* Buy & Hold line (orange) */}
                    <polyline
                      fill="none"
                      stroke="#f97316"
                      strokeWidth="2"
                      strokeDasharray="4"
                      points={backtest.history.map((h, i) => {
                        const x = (i / (backtest.history!.length - 1)) * 300;
                        const minVal = Math.min(...backtest.history!.map(h => Math.min(h.strategy_value, h.buyhold_value, h.bond_value)));
                        const maxVal = Math.max(...backtest.history!.map(h => Math.max(h.strategy_value, h.buyhold_value, h.bond_value)));
                        const y = 100 - ((h.buyhold_value - minVal) / (maxVal - minVal)) * 100;
                        return `${x},${y}`;
                      }).join(' ')}
                    />
                    
                    {/* Bond line (pink) */}
                    <polyline
                      fill="none"
                      stroke="#f472b6"
                      strokeWidth="2"
                      strokeDasharray="2"
                      points={backtest.history.map((h, i) => {
                        const x = (i / (backtest.history!.length - 1)) * 300;
                        const minVal = Math.min(...backtest.history!.map(h => Math.min(h.strategy_value, h.buyhold_value, h.bond_value)));
                        const maxVal = Math.max(...backtest.history!.map(h => Math.max(h.strategy_value, h.buyhold_value, h.bond_value)));
                        const y = 100 - ((h.bond_value - minVal) / (maxVal - minVal)) * 100;
                        return `${x},${y}`;
                      }).join(' ')}
                    />
                  </svg>
                  
                  {/* Final values - outside chart */}
                  <div className="absolute right-0 top-0 bottom-0 w-12 flex flex-col justify-between py-1 text-[10px] font-medium">
                    <div className="text-cyan-400 bg-zinc-900/80 px-1 rounded">{backtest.history[backtest.history.length - 1].strategy_value}</div>
                    <div className="text-pink-400 bg-zinc-900/80 px-1 rounded">{backtest.history[backtest.history.length - 1].bond_value}</div>
                    <div className="text-orange-400 bg-zinc-900/80 px-1 rounded">{backtest.history[backtest.history.length - 1].buyhold_value}</div>
                  </div>
                </div>
                
                {/* Legend */}
                <div className="flex justify-center gap-4 mt-2 text-[10px]">
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-cyan-400"></span>
                    <span className="text-zinc-300">AI Strategy</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-orange-400" style={{borderStyle: 'dashed'}}></span>
                    <span className="text-zinc-300">PEA-E 100%</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-pink-400"></span>
                    <span className="text-zinc-300">PEA-F 100%</span>
                  </span>
                </div>
              </div>
            )}
            
            {/* Allocation History */}
            {backtest.history && backtest.history.length > 0 && (
              <div className="mt-3 p-3 rounded-xl bg-zinc-900/50">
                <p className="text-[10px] sm:text-xs text-zinc-400 mb-2">สัดส่วน PEA-E ที่แนะนำแต่ละเดือน</p>
                <div className="flex gap-1 overflow-x-auto pb-1">
                  {backtest.history.map((h, i) => (
                    <div key={i} className="flex flex-col items-center min-w-[28px]">
                      <div 
                        className={`w-5 rounded-t text-[8px] flex items-end justify-center ${h.correct ? 'bg-cyan-500/60' : 'bg-pink-500/60'}`}
                        style={{ height: `${h.allocation * 0.4}px` }}
                      >
                        {h.allocation > 50 && <span className="text-white/80">{h.allocation}</span>}
                      </div>
                      <div className="text-[8px] text-zinc-500 mt-1">{h.date.slice(-2)}</div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-center gap-3 mt-2 text-[9px] text-zinc-400">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-sm bg-cyan-500/60"></span> ทายถูก
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-sm bg-pink-500/60"></span> ทายผิด
                  </span>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Collapsible Details Section */}
        {prediction.ml_features && (
          <section className="pt-5 sm:pt-6 border-t border-zinc-800/50 animate-fade-in-up delay-500">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="w-full flex items-center justify-between text-[11px] sm:text-xs text-zinc-300 py-2 hover:text-white transition-colors group"
              aria-expanded={showDetails}
            >
              <span className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full transition-colors ${showDetails ? 'bg-cyan-400' : 'bg-zinc-600'}`} />
                รายละเอียดเพิ่มเติม
              </span>
              <svg 
                className={`w-4 h-4 chevron-rotate ${showDetails ? 'open' : ''}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {showDetails && (
              <div className="space-y-5 pt-2 animate-slide-down">
                {/* ML Features */}
                <div aria-label="ตัวชี้วัด ML">
                  <p className="text-[11px] sm:text-xs text-zinc-400 mb-3">ตัวชี้วัดที่ใช้ในโมเดล</p>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="p-2 rounded-lg bg-zinc-900/50 animate-pop-in" style={{ animationDelay: '100ms' }}>
                      <div className="text-zinc-300 mb-1">RSI (6)</div>
                      <div className={`font-medium tabular-nums ${
                        prediction.ml_features.RSI_6 < 35 ? 'text-cyan-400' : 
                        prediction.ml_features.RSI_6 > 65 ? 'text-pink-400' : 'text-white'
                      }`}>
                        {prediction.ml_features.RSI_6}
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-zinc-900/50 animate-pop-in" style={{ animationDelay: '200ms' }}>
                      <div className="text-zinc-300 mb-1">ผลตอบแทน 3 เดือน</div>
                      <div className={`font-medium tabular-nums ${
                        prediction.ml_features.Return_3m >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {prediction.ml_features.Return_3m > 0 ? '+' : ''}{prediction.ml_features.Return_3m}%
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-zinc-900/50 animate-pop-in" style={{ animationDelay: '300ms' }}>
                      <div className="text-zinc-300 mb-1">ความผันผวน</div>
                      <div className="font-medium tabular-nums text-white">
                        {prediction.ml_features.Volatility_3m}%
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-zinc-900/50 animate-pop-in" style={{ animationDelay: '400ms' }}>
                      <div className="text-zinc-300 mb-1">ผลตอบแทน 1 เดือน</div>
                      <div className={`font-medium tabular-nums ${
                        prediction.ml_features.Return_1m >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {prediction.ml_features.Return_1m > 0 ? '+' : ''}{prediction.ml_features.Return_1m}%
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-zinc-900/50 animate-pop-in" style={{ animationDelay: '500ms' }}>
                      <div className="text-zinc-300 mb-1">ราคา vs SMA6</div>
                      <div className={`font-medium tabular-nums ${
                        prediction.ml_features.Price_SMA6_Ratio >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {prediction.ml_features.Price_SMA6_Ratio > 0 ? '+' : ''}{prediction.ml_features.Price_SMA6_Ratio}%
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-zinc-900/50 animate-pop-in" style={{ animationDelay: '600ms' }}>
                      <div className="text-zinc-300 mb-1">Drawdown</div>
                      <div className={`font-medium tabular-nums ${
                        prediction.ml_features.Drawdown >= -5 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {prediction.ml_features.Drawdown}%
                      </div>
                    </div>
                  </div>
                </div>

                {/* Model Votes */}
                {prediction.ml_details?.individual_models && (
                  <div aria-label="การโหวตของโมเดล">
                    <p className="text-[11px] sm:text-xs text-zinc-400 mb-3">การโหวตของโมเดล</p>
                    <div className="space-y-2">
                      {Object.entries(prediction.ml_details.individual_models).map(([name, model]: [string, any], index) => {
                        const modelNames: Record<string, string> = {
                          'xgb': 'XGBoost',
                          'rf': 'Random Forest',
                          'gb': 'Gradient Boosting'
                        };
                        const isBull = model.prediction === 1;
                        return (
                          <div 
                            key={name} 
                            className="flex items-center gap-3 text-xs sm:text-sm animate-stagger-in"
                            style={{ animationDelay: `${index * 80}ms` }}
                          >
                            <span className="w-28 sm:w-32 text-zinc-300">{modelNames[name] || name}</span>
                            <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                              <div 
                                className={`h-full rounded-full signal-bar ${isBull ? 'bg-cyan-400' : 'bg-pink-400'}`}
                                style={{ 
                                  '--signal-width': `${model.confidence * 100}%`,
                                  animationDelay: `${index * 100 + 200}ms`
                                } as React.CSSProperties}
                              />
                            </div>
                            <span className={`w-20 text-right tabular-nums ${isBull ? 'text-cyan-400' : 'text-pink-400'}`}>
                              {isBull ? 'ขึ้น' : 'ลง'} {Math.round(model.confidence * 100)}%
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Additional Backtest Metrics */}
                {backtest?.metrics && (
                  <div aria-label="รายละเอียด Backtest">
                    <p className="text-[11px] sm:text-xs text-zinc-400 mb-3">รายละเอียด Backtest</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2 rounded-lg bg-zinc-900/50">
                        <span className="text-zinc-300">จำนวนเดือน:</span>
                        <span className="float-right text-white">{backtest.metrics.total_trades}</span>
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-900/50">
                        <span className="text-zinc-300">ทายถูก:</span>
                        <span className="float-right text-white">{backtest.metrics.correct_trades}</span>
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-900/50">
                        <span className="text-zinc-300">Max Drawdown:</span>
                        <span className="float-right text-red-400">{backtest.metrics.max_drawdown_pct}%</span>
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-900/50">
                        <span className="text-zinc-300">Buy & Hold:</span>
                        <span className={`float-right ${backtest.returns?.buy_hold_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {backtest.returns?.buy_hold_return_pct > 0 ? '+' : ''}{backtest.returns?.buy_hold_return_pct}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* Footer */}
        <footer className="text-center pt-6 sm:pt-8 space-y-3 sm:space-y-4 pb-4 animate-fade-in-up delay-700">
          <p className="text-[11px] sm:text-xs text-zinc-400">ใช้ประกอบการตัดสินใจเท่านั้น</p>
          
          <div className="text-[11px] sm:text-xs text-zinc-300 space-y-2 pt-3 sm:pt-4 border-t border-zinc-800/50">
            <p className="text-zinc-200 font-medium">เกี่ยวกับโมเดล</p>
            <p>
              ใช้ <span className="text-white">{data?.model_info?.type || "ML Ensemble"}</span> วิเคราะห์ข้อมูลรายเดือน
            </p>
            <p className="leading-relaxed">
              อิงจาก SET50 ({data?.model_info?.ticker || "^SET50"}) โดยใช้ features: Return, SMA Ratio, RSI, Volatility, Drawdown
            </p>
            <div className="pt-2 space-y-1">
              <p><span className="text-cyan-400">PEA-E</span> = กองทุนหุ้น อิงจาก SET50 (TDEX)</p>
              <p><span className="text-pink-400">PEA-F</span> = กองทุนตราสารหนี้ อิงจาก Bond Yield</p>
            </div>
            <p className="pt-2 text-zinc-400">
              สัดส่วนคำนวณจากความมั่นใจของ ML Ensemble (XGB + RF + GB)
            </p>
          </div>
        </footer>
      </div>

      {/* Screen reader announcements */}
      <div aria-live="assertive" className="sr-only">
        {refreshing && "กำลังรีเฟรชข้อมูล"}
      </div>
    </main>
  );
}

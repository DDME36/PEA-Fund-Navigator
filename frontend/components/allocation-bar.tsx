"use client";

interface AllocationBarProps {
  equityPercent: number;
}

export function AllocationBar({ equityPercent }: AllocationBarProps) {
  const bondPercent = 100 - equityPercent;
  
  return (
    <div className="space-y-4">
      {/* Large numbers display */}
      <div className="flex justify-between items-center">
        <div className="text-center">
          <p className="text-xs text-muted-foreground mb-1">🚀 PEA-E (หุ้น)</p>
          <p className="text-4xl font-bold text-bullish">{equityPercent}%</p>
        </div>
        <div className="text-2xl text-muted-foreground">:</div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground mb-1">🛡️ PEA-F (ตราสารหนี้)</p>
          <p className="text-4xl font-bold text-blue-400">{bondPercent}%</p>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="h-8 rounded-full overflow-hidden flex bg-muted">
        <div
          className="bg-gradient-to-r from-bullish to-emerald-400 transition-all duration-700 flex items-center justify-center text-sm font-bold text-white"
          style={{ width: `${equityPercent}%` }}
        >
          {equityPercent >= 15 && `PEA-E`}
        </div>
        <div
          className="bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-700 flex items-center justify-center text-sm font-bold text-white"
          style={{ width: `${bondPercent}%` }}
        >
          {bondPercent >= 15 && `PEA-F`}
        </div>
      </div>
      
      <p className="text-xs text-muted-foreground text-center">
        📊 สัดส่วนแนะนำ (รวม 100%) สำหรับกองทุนสำรองเลี้ยงชีพ
      </p>
    </div>
  );
}

import type {
  PredictionResponse,
  BacktestResponse,
} from "./types";

// Static data URL - อ่านจาก JSON file ที่ถูก generate โดย daily_update.py
const DATA_URL = "/data/prediction.json";

export interface DailyData {
  updated_at: string;
  updated_timestamp: string;
  prediction: PredictionResponse | null;
  backtest: BacktestResponse | null;
  model_info: {
    type: string;
    ticker: string;
  };
  error?: string;
}

/**
 * โหลดข้อมูลจาก static JSON
 * ข้อมูลนี้ถูก generate โดย scripts/daily_update.py
 */
export async function getDailyData(): Promise<DailyData> {
  const res = await fetch(DATA_URL, {
    // ไม่ cache เพื่อให้ได้ข้อมูลล่าสุดเสมอ
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to load data: ${res.status}`);
  }

  return res.json();
}

/**
 * Format วันที่อัพเดทให้อ่านง่าย
 */
export function formatUpdatedAt(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString("th-TH", {
      timeZone: "Asia/Bangkok",
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return timestamp;
  }
}

/**
 * คำนวณว่าข้อมูลเก่าแค่ไหน
 */
export function getDataAge(timestamp: string): string {
  try {
    const updated = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - updated.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays} วันที่แล้ว`;
    } else if (diffHours > 0) {
      return `${diffHours} ชั่วโมงที่แล้ว`;
    } else {
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return diffMins > 0 ? `${diffMins} นาทีที่แล้ว` : "เมื่อสักครู่";
    }
  } catch {
    return "";
  }
}
